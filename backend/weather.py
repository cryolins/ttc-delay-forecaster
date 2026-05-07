import httpx
import pandas as pd
from datetime import datetime
from schemas import PredictRequest

WEATHER_COORDS = [43.711158, -79.377118] # eglinton / bayview, approximately centre of city
HIST_METEO_URL = "https://archive-api.open-meteo.com/v1/archive"
FORE_METEO_URL = "https://api.open-meteo.com/v1/forecast"

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

async def weather_from_req(req: PredictRequest):
    params = {
        "latitude": WEATHER_COORDS[0],
        "longitude": WEATHER_COORDS[1],
        "start_date": req.timestamp.strftime("%Y-%m-%d"),
        "end_date":  req.timestamp.strftime("%Y-%m-%d"),
        "hourly": [
            "temperature_2m",
            "precipitation",
            "snowfall",
            "windspeed_10m",
            "weathercode"
        ],
        "timezone": "America/Toronto"
    }

    # api route should already prevent overly old or new dates, 
    # so just calculate if using historical or forecast
    now = datetime.now()
    weather_url = FORE_METEO_URL
    if ((now - req.timestamp).days > 14):
        # if older than 2 weeks we should be able to call archive
        weather_url = HIST_METEO_URL

    # get the data
    async with httpx.AsyncClient() as client:
        res = await client.get(weather_url, params=params, timeout=15)
        res.raise_for_status()

    # put data into dataframe to convert types easily
    data = res.json()
    df = pd.DataFrame(data["hourly"])
    df["time"] = pd.to_datetime(df["time"])
    df = df.rename(columns={"time": "datetime", "weathercode": "weather_code"})

    # convert wmo code to custom category
    df["weather_category"] = df["weather_code"].apply(bucket_wcs)
    df.drop(columns="weather_code", inplace=True)

    # match the hour and return
    hour_row = df[df["datetime"].dt.hour == req.timestamp.hour]
    if (len(hour_row) == 0):
        raise ValueError(f"Hour {req.timestamp.hour} not found in Open-Meteo response.")
    hour_row_dict = hour_row.to_dict(orient="records")[0]
    return hour_row_dict
