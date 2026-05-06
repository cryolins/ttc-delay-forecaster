import pandas as pd
from pathlib import Path

# this file is a script that generates any small pieces of data that the backend requires

DATA_DIR_PATH = Path(__file__).resolve().parent.parent.parent / "data"
BACK_DATA_DIR_PATH = Path(__file__).resolve().parent.parent.parent / "backend" / "backend-data"

def process_dirs(df: pd.DataFrame):
    # process directions
    dirs = df.groupby(["route", "direction"])["direction"].value_counts().reset_index()
    dirs = dirs[((dirs["route"] < 500) | (dirs["route"] >= 600))] # just in case, remove streetcars

    # get top 3 directions per route and its count, and save it in a json
    # assumes the groups are already sorted by count, descending
    def get_dir_and_count(group):
        return list(zip(group["direction"], group["count"]))[:3]

    dirs = (dirs
        .sort_values("count", ascending=False)
        .groupby("route")
        .apply(get_dir_and_count)
        .rename("dirs")
    )
    dirs.to_json(BACK_DATA_DIR_PATH / "route_dirs.json", orient="index")

def process_incidents(df: pd.DataFrame):
    # process incident types
    incidents = df.groupby(["route", "incident_type"])["incident_type"].value_counts().reset_index()

    # get top 5 incident types per route and its ratio weight, and save it in a json
    # assumes the groups are already sorted by count, descending
    def get_dir_and_count(group):
        top_5_total = sum(list(group["count"])[:5])
        return list(zip(group["incident_type"], group["count"] / top_5_total))[:5]

    incidents = (incidents
        .sort_values("count", ascending=False)
        .groupby("route")
        .apply(get_dir_and_count)
        .rename("incidents")
    )
    incidents.to_json(BACK_DATA_DIR_PATH / "route_top_incidents.json", orient="index")

def get_routes(df: pd.DataFrame):
    # gets route info (route name for now) and loads it onto a json
    routes_df = pd.read_csv(DATA_DIR_PATH / "routes.csv", usecols=["route_id", "route_long_name"])
    valid_routes = df["route"]
    routes = (
        routes_df[routes_df["route_id"].isin(valid_routes)]
        .sort_values("route_id")
        .set_index("route_id")["route_long_name"]
    )
    routes.to_json(BACK_DATA_DIR_PATH / "route_info.json", orient="index")

# load in df
df = (
        pd.read_csv(DATA_DIR_PATH / "final-input.csv", parse_dates=["datetime"])
        .reset_index(drop=True)
        .drop(columns=["Unnamed: 0"])
    )

process_dirs(df)
process_incidents(df)
get_routes(df)
