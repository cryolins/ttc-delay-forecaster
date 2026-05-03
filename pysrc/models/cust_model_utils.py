from pathlib import Path
import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
from xgboost import XGBRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, root_mean_squared_error

DATA_DIR_PATH = Path(__file__).resolve().parent.parent.parent / "data"
RESULTS_DIR_PATH = Path(__file__).resolve().parent.parent.parent / "model-results"

NUM_FEATURES = ["route_stops", "route_length", "dt_dist_mean", "dt_dist_std", 
                "temperature_2m", "precipitation", "snowfall", "windspeed_10m",
                "is_weekend", "is_rush_hour", "is_holiday", 
                "day_sin", "day_cos", "hour_sin", "hour_cos", "month_sin", "month_cos"]
CYC_FEATURES = ["day", "hour", "month"]
CYC_MAXES = [7, 24, 12]
CAT_FEATURES = ["route", "incident_type", "direction", "weather_category"]

def load_data():
    df = (
        pd.read_csv(DATA_DIR_PATH / "final-input.csv", parse_dates=["datetime"])
        .sort_values("datetime")
        .reset_index(drop=True)
        .drop(columns=["Unnamed: 0"])
    )

    # checking counts per year
    # by_year = df.copy()
    # by_year["year"] = by_year["datetime"].dt.year
    # print(by_year.groupby("year").count())

    return df

def common_preprocess(df: pd.DataFrame):
    def encode_cyclic(df: pd.DataFrame, col, max_val):
        df[f"{col}_sin"] = np.sin(2 * np.pi * df[col] / max_val)
        df[f"{col}_cos"] = np.cos(2 * np.pi * df[col] / max_val)
        return df.drop(columns=col)
    def encode_str_cat(df: pd.DataFrame, col):
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        return df

    for i in range(len(CYC_FEATURES)):
        df = encode_cyclic(df, CYC_FEATURES[i], CYC_MAXES[i])

    for i in range(1, len(CAT_FEATURES)):
        df = encode_str_cat(df, CAT_FEATURES[i])

    return df

def target_encode_route(df: pd.DataFrame):
    route_means = df.groupby("route")["min_delay"].mean()
    df["route"] = df["route"].map(route_means)
    return df


def split_data(df: pd.DataFrame, incl_val=True, encode_route=True):
    if not incl_val:
        train = df[df["datetime"].dt.year < 2024]
        test  = df[df["datetime"].dt.year >= 2024]

        if encode_route:
            train = target_encode_route(train)
            test = target_encode_route(train)

        X_train = train.drop(columns=["min_delay", "datetime"])
        y_train = train["min_delay"]
        X_test = test.drop(columns=["min_delay", "datetime"])
        y_test = test["min_delay"]
        return (train, test, X_train, y_train, X_test, y_test)
    
    else:
        train = df[df["datetime"].dt.year < 2023]
        val   = df[(df["datetime"].dt.year >= 2023) & (df["datetime"].dt.year < 2024)]
        test  = df[df["datetime"].dt.year >= 2024]

        if encode_route:
            train = target_encode_route(train)
            val = target_encode_route(val)
            test = target_encode_route(train)

        X_train= train.drop(columns=["min_delay", "datetime"])
        y_train = train["min_delay"]
        X_val = val.drop(columns=["min_delay", "datetime"])
        y_val = val["min_delay"]
        X_test = test.drop(columns=["min_delay", "datetime"])
        y_test = test["min_delay"]
        return (train, val, test, X_train, y_train, X_val, y_val, X_test, y_test)

def compute_metrics(y_test, y_pred):
    return {
        "mae":  round(mean_absolute_error(y_test, y_pred), 4),
        "rmse": round(root_mean_squared_error(y_test, y_pred), 4)
    }

def save_metrics(metrics: dict, name):
    with open(RESULTS_DIR_PATH / f"{name}.json", "w") as f:
        json.dump(metrics, f, indent=2)

def visualize_preds(test: pd.DataFrame, y_test, y_pred, img_name = None):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # scatter: predicted vs actual
    axes[0].scatter(y_test, y_pred, alpha=0.3, s=10, color="steelblue")
    axes[0].plot(
        [y_test.min(), y_test.max()],
        [y_test.min(), y_test.max()],
        "r--", linewidth=1.5, label="Perfect prediction"
    )
    axes[0].set_xlabel("Actual Delay (min)")
    axes[0].set_ylabel("Predicted Delay (min)")
    axes[0].set_title("Predicted vs Actual")
    axes[0].legend()

    # residuals: errors over time
    residuals = y_test.values - y_pred
    axes[1].plot(test["datetime"].values, residuals, alpha=0.4, linewidth=0.5, color="coral")
    axes[1].axhline(0, color="black", linewidth=1, linestyle="--")
    axes[1].set_xlabel("Date")
    axes[1].set_ylabel("Residual (Actual - Predicted)")
    axes[1].set_title("Residuals Over Time")

    plt.tight_layout()
    if img_name:
        plt.savefig(RESULTS_DIR_PATH / f"{img_name}.png", dpi=150)
    else:
        plt.show()

def visualize_key_features(xgb_model: XGBRegressor, img_name):
    features = NUM_FEATURES + CAT_FEATURES
    importances = pd.Series(
    xgb_model.feature_importances_,
        index=features
    ).sort_values(ascending=True)

    fig, ax = plt.subplots(figsize=(8, 6))
    importances.plot(kind="barh", ax=ax, color="steelblue", edgecolor="white")
    ax.set_title("XGBoost Feature Importances")
    ax.set_xlabel("Importance Score")
    ax.axvline(x=0, color="black", linewidth=0.8)
    plt.tight_layout()
    if img_name:
        plt.savefig(RESULTS_DIR_PATH / f"{img_name}.png", dpi=150)
    else:
        plt.show()
