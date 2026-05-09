import pandas as pd
import numpy as np
import holidays

NUM_FEATURES = ["route", "route_stops", "route_length", "dt_dist_mean", "dt_dist_std", 
                "temperature_2m", "precipitation", "snowfall", "windspeed_10m",
                "is_weekend", "is_rush_hour", "is_holiday", 
                "day_sin", "day_cos", "hour_sin", "hour_cos", "month_sin", "month_cos"]
CYC_FEATURES = ["day", "hour", "month"]
CYC_MAXES = [7, 24, 12]
CAT_FEATURES = ["incident_type", "direction", "weather_category"]
FEATURES = NUM_FEATURES + CAT_FEATURES

def get_time_features(df: pd.DataFrame, holiday_year: int):
    # transforms dataframe by extracting model features from a "datetime" column
    df["hour"] = df["datetime"].dt.hour # simplify time to hour
    df["day"] = df["datetime"].dt.dayofweek
    df["month"] = df["datetime"].dt.month
    df["is_weekend"]  = df["datetime"].dt.dayofweek >= 5
    df["is_rush_hour"] = df["hour"].isin([7, 8, 9, 16, 17, 18, 19])
    ont_holidays = holidays.country_holidays("CA", "ON", years=holiday_year)
    df["is_holiday"] = df["datetime"].dt.date.isin(ont_holidays)

    return df

# same preprocessing step as used in model training for cyclic and label encoding
def preprocess(df: pd.DataFrame):
    def encode_cyclic(df: pd.DataFrame, col, max_val):
        df[f"{col}_sin"] = np.sin(2 * np.pi * df[col] / max_val)
        df[f"{col}_cos"] = np.cos(2 * np.pi * df[col] / max_val)
        return df.drop(columns=col)
    def encode_str_cat(df: pd.DataFrame, col: str):
        df[col] = df[col].astype("category")
        return df

    for i in range(len(CYC_FEATURES)):
        df = encode_cyclic(df, CYC_FEATURES[i], CYC_MAXES[i])

    for cat_feat in CAT_FEATURES:
        df = encode_str_cat(df, cat_feat)

    return df
