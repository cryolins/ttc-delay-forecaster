import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.metrics.pairwise import haversine_distances

# this file takes in a cleaned bus delay data csv and gtfs csvs to attach all required features

DATA_DIR_PATH = Path(__file__).resolve().parent.parent.parent / "data"

delay_df = pd.read_csv(DATA_DIR_PATH / "bus-delay-cleaned.csv")
routes_df = pd.read_csv(DATA_DIR_PATH / "routes.csv")

# join to keep only valid route numbers
valid_routes = routes_df["route_id"]
delay_df = pd.merge(delay_df, valid_routes, left_on="Route", right_on="route_id", how="inner")
delay_df.drop(columns=["Unnamed: 0"], inplace=True)
delay_df = delay_df[delay_df["route_id"] > 6] # delete any subways that sneaked in
delay_df.info()

# trips data unaggregated
trips_df: pd.DataFrame = (
    pd.read_csv(DATA_DIR_PATH / "trips.csv", usecols=["route_id", "service_id", "trip_id"])
    .loc[lambda df: df["service_id"] < 10]
    .drop(columns="service_id")
)

# get distances from gtfs data
DOWNTOWN_POINT = [43.65472, -79.38827] # dundas and university, decent centre for downtown
stops_df = pd.read_csv(DATA_DIR_PATH / "stops.csv", usecols=["stop_id", "stop_lat", "stop_lon"])
stop_times_df = (
    pd.merge(pd.read_csv(DATA_DIR_PATH / "stop_times.csv", usecols=["trip_id", "stop_id", "stop_sequence", "shape_dist_traveled"]),
             trips_df["trip_id"].drop_duplicates(), how="inner", on="trip_id")  
) # immediately filter out unnecessary data to reduce memory

# step to select a trip for a route based on 80th percentile in length
# ensures something decently long but probably not an outlier
def get_percentile_row(group, q=0.8):
    idx = int(q * len(group)) - 1
    return group.iloc[idx]

select_trip_df = (
    pd.merge(stop_times_df, trips_df, how="inner", on="trip_id")
    .groupby("trip_id")
    .agg(trip_length=("shape_dist_traveled", "max"), route_id=("route_id", "first"))
    .reset_index()
    .sort_values("trip_length")
    .groupby("route_id")
    .apply(get_percentile_row)
    .reset_index()
)

# now merge stop_times with selected trips, so even less trips saved and memory used
stop_times_df = pd.merge(stop_times_df, select_trip_df["trip_id"].drop_duplicates(), how="inner", on="trip_id")
# merge delay df with select trip df to supply it with trip_id and route length information
df = pd.merge(delay_df, select_trip_df, on="route_id", how="inner")
df.info()

route_trip_df = pd.merge(stop_times_df, stops_df, on="stop_id", how="inner")
route_trip_df["dt_dists"] = haversine_distances(np.radians(route_trip_df[["stop_lat", "stop_lon"]]), [np.radians(DOWNTOWN_POINT)]) * 6371
route_trip_df = route_trip_df.groupby("trip_id").agg(
    route_stops=("stop_sequence", "max"),
    dt_dist_mean=("dt_dists", "mean"),
    dt_dist_std=("dt_dists", "std")
)
df = (
    pd.merge(df, route_trip_df, on="trip_id", how="inner")
    .drop(columns=["route_id", "trip_id"])
    .rename(columns={
        "Route": "route",
        "Time": "time",
        "Day": "day",
        "Incident": "incident_type",
        "Direction": "direction",
        "Date": "date",
        "Min Delay": "min_delay",
        "trip_length": "route_length"
    })
)
df.info()
df.to_csv(DATA_DIR_PATH / "bus-delay-gtfs.csv")
