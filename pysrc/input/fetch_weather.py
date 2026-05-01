import requests
import pandas as pd
from pathlib import Path

# this file calls the OpenMeteo archive API for the time period being analyzed and saves it in data

WEATHER_COORDS = [43.711158, -79.377118] # eglinton / bayview, approximately centre of city
START_DATE = "2020-01-01"
END_DATE = "2024-12-31"
OPEN_METEO_URL = "https://archive-api.open-meteo.com/v1/archive"
DATA_DIR_PATH = Path(__file__).resolve().parent.parent.parent / "data"

params = {
        "latitude": WEATHER_COORDS[0],
        "longitude": WEATHER_COORDS[1],
        "start_date": START_DATE,
        "end_date": END_DATE,
        "hourly": [
            "temperature_2m",
            "precipitation",
            "snowfall",
            "windspeed_10m",
            "weathercode"
        ],
        "timezone": "America/Toronto"
    }

res = requests.get(OPEN_METEO_URL, params)
res.raise_for_status() # raise error for the script if any
data = res.json()
df = pd.DataFrame(data["hourly"])
df["time"] = pd.to_datetime(df["time"])
df = df.rename(columns={"time": "datetime", "weathercode": "weather_code"})

# bucket weather codes
def bucket_wcs(wc: int):
    if (wc <= 1):
        return "clear"
    elif (wc <= 3):
        return "cloudy"
    elif (wc <= 10 or (wc >= 30 and wc <= 35)):
        return "dusty"
    elif (wc <= 12 or (wc >= 40 and wc <= 49)):
        return "fog"
    elif (wc < 30):
        return "previous" # precipitation happened in previous hour
    elif ((wc >= 36 and wc <= 39) or (wc >= 70 and wc <= 79)):
        return "snow"
    elif (wc <= 82):
        return "rain"
    else:
        return "mixed"
    
df["weather_category"] = df["weather_code"].apply(bucket_wcs)

df.info()

df.to_csv(DATA_DIR_PATH / "weather-source.csv")
