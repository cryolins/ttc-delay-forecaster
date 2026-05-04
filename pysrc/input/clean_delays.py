import pandas as pd
import numpy as np
from pathlib import Path

# this file takes in raw bus delay data and cleans it into a csv

DATA_DIR_PATH = Path(__file__).resolve().parent.parent.parent / "data"

# read bus delay data files
START_YEAR = 2020
yearly_dfs: list[pd.DataFrame] = []
for i in range(5):
    yearly_sheets = pd.read_excel(DATA_DIR_PATH / f"ttc-bus-delay-data-{START_YEAR + i}.xlsx", sheet_name=None)
    yearly_df = pd.concat(yearly_sheets.values(), ignore_index=True)
    yearly_dfs.append(yearly_df)

delay_df = pd.concat(yearly_dfs, ignore_index=True)

# combine renamed columns
delay_df["Date"] = delay_df["Date"].combine_first(delay_df["Report Date"])
delay_df["Min Delay"] = delay_df["Min Delay"].combine_first(delay_df["Delay"])
delay_df["Min Gap"] = delay_df["Min Gap"].combine_first(delay_df["Gap"])
# Line and Bound fields are from Jul/Aug 2021 when streetcar data was given instead of bus data

# standardize the labels in direction field via np.select
dir_conds = [
    delay_df["Direction"].str.upper().str.contains("N"),
    delay_df["Direction"].str.upper().str.contains("E"),
    delay_df["Direction"].str.upper().str.contains("S"),
    delay_df["Direction"].str.upper().str.contains("W"),
]
dir_choices = ["N", "E", "S", "W"]
delay_df["Direction"] = np.select(dir_conds, dir_choices, default="B")

# drop unnecessary columns
delay_df.drop(columns=["Min Gap", "Report Date", "Delay", "Gap", "Location", "Vehicle", "Line", "Bound", "Unnamed: 10"], inplace=True)
# min gap seems to be highly correlated to min delay (the gap is likely describing the gap caused by the delay)
# so we remove it

# convert select columns to correct types
delay_df["Route"] = pd.to_numeric(delay_df["Route"], errors="coerce")
time1 = pd.to_datetime(delay_df["Time"], errors="coerce", format="%H:%M")
time2 = pd.to_datetime(delay_df["Time"], errors="coerce", format="%H:%M:%S")
delay_df["Time"] = time1.combine_first(time2).dt.time

# remove null values
delay_df.dropna(inplace=True)

# categorize incident types
inc_conds = [
    delay_df["Incident"].str.lower().str.contains("late"),
    delay_df["Incident"].str.lower().str.contains("mechanical"),
    delay_df["Incident"].str.lower().str.contains("operat"),
    delay_df["Incident"].str.lower().str.contains("securit"),
    delay_df["Incident"].str.lower().str.contains("block"),
    delay_df["Incident"].str.lower().str.contains("collision"),
    delay_df["Incident"].str.lower().str.contains("diversion"),
    delay_df["Incident"].str.lower().str.contains("off route"),
    delay_df["Incident"].str.lower().str.contains("emergency services"),
    delay_df["Incident"].str.lower().str.contains("cleaning"),
    delay_df["Incident"].str.lower().str.contains("vision"),
]
inc_choices = [
    "late exit",
    "mechanical",
    "operations",
    "security",
    "road blocked",
    "collision",
    "diversion",
    "off route",
    "emergency services",
    "cleaning",
    "vision"
]
delay_df["Incident"] = np.select(inc_conds, inc_choices, default="general")

# remove delays above 1h as they are more extreme circumstances the model is not expected to predict
delay_df = delay_df[delay_df["Min Delay"] <= 60]

# convert select columns to integers
delay_df["Route"] = delay_df["Route"].astype("int64")
delay_df["Min Delay"] = delay_df["Min Delay"].astype("int64")

# output to cleaned csv
delay_df.info()
delay_df.to_csv(DATA_DIR_PATH / "bus-delay-cleaned.csv")
