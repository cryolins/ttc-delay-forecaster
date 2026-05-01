import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.metrics.pairwise import haversine_distances

# this file takes in a cleaned bus delay data csv and gtfs csvs to attach all required features

DATA_DIR_PATH = Path(__file__).resolve().parent.parent / "data"

delay_df = pd.read_csv(DATA_DIR_PATH / "bus-delay-cleaned.csv")
routes_df = pd.read_csv(DATA_DIR_PATH / "routes.csv")

# join to keep only valid route numbers
valid_routes = routes_df["route_id"]
delay_df = pd.merge(delay_df, valid_routes, left_on="Route", right_on="route_id", how="inner")
delay_df.drop(columns=["Unnamed: 0"], inplace=True)
delay_df = delay_df[delay_df["route_id"] > 6] # delete any subways that sneaked in
delay_df.info()

# get sample trip per route from trips data
trip_by_route_df = (
    pd.read_csv(DATA_DIR_PATH / "trips.csv")
    .loc[lambda df: df["service_id"] < 10]
    .groupby("route_id")
    .agg({
        "trip_id": "last",
        #"shape_id": "last"
    })
)
df = pd.merge(delay_df, trip_by_route_df, on="route_id", how="inner")
df.info()

# get distances from gtfs data
DOWNTOWN_POINT = [43.65472, -79.38827] # dundas and university, decent centre for downtown
stops_df = pd.read_csv(DATA_DIR_PATH / "stops.csv", usecols=["stop_id", "stop_lat", "stop_lon"])
stop_times_df = (
    pd.merge(pd.read_csv(DATA_DIR_PATH / "stop_times.csv", usecols=["trip_id", "stop_id", "stop_sequence", "shape_dist_traveled"]),
             df["trip_id"].drop_duplicates(), how="inner", on="trip_id")  
) # immediately filter out unnecessary data to reduce memory

route_trip_df = pd.merge(stop_times_df, stops_df, on="stop_id", how="inner")
route_trip_df["dt_dists"] = haversine_distances(np.radians(route_trip_df[["stop_lat", "stop_lon"]]), [np.radians(DOWNTOWN_POINT)]) * 6371
route_trip_df = route_trip_df.groupby("trip_id").agg(
    route_stops=("stop_sequence", "max"),
    route_length=("shape_dist_traveled", "max"),
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
        "Min Gap": "min_gap"
    })
)
df.info()
df.to_csv(DATA_DIR_PATH / "bus-delay-gtfs.csv")
