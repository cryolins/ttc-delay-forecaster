import pandas as pd
from pathlib import Path
import holidays

DATA_DIR_PATH = Path(__file__).resolve().parent.parent / "data"
WEATHER_COORDS = [43.711158, -79.377118] # eglinton / bayview, approximately centre of city

delay_df = pd.read_csv(DATA_DIR_PATH / "bus-delay-gtfs.csv").drop(columns="Unnamed: 0")
weather_df = pd.read_csv(DATA_DIR_PATH / "weather-source.csv").drop(columns="Unnamed: 0")

# set datetime field to join with, then join them
delay_df["datetime"] = pd.to_datetime(delay_df["date"].astype(str) + " " 
                                      + delay_df["time"].astype(str).str.slice_replace(-6, repl=":00:00"))
weather_df["datetime"] = pd.to_datetime(weather_df["datetime"])
df = pd.merge(delay_df, weather_df, on="datetime", how="left")

# regenerating certain columns by datetime column to ensure standardization
df["hour"] = df["datetime"].dt.hour # simplify time to hour
df["day"] = df["datetime"].dt.dayofweek
df["month"] = df["datetime"].dt.month
df["is_weekend"]  = df["datetime"].dt.dayofweek >= 5
df["is_rush_hour"] = df["hour"].isin([7, 8, 9, 16, 17, 18, 19])
    # we are considering trends over a year, so no year column saved

ont_holidays = holidays.country_holidays("CA", "ON", years=range(2020, 2025))
df["is_holiday"] = df["datetime"].dt.date.isin(ont_holidays)

df.drop(columns=["date", "time", "datetime", "weather_code"], inplace=True)

df.info()
df.to_csv(DATA_DIR_PATH / "final-input.csv")
