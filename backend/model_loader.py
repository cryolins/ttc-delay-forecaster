import joblib
from pathlib import Path

MODEL_PATH = Path("./model/delay_model_V3-1.pkl")
FEATURES_PATH = Path("./model/feature_cols.pkl")

# set up global exports
model = None
feature_cols = None

# function to load in these variables
def load_model():
    global model, feature_cols
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"No model found at {MODEL_PATH}.")
    elif not FEATURES_PATH.exists():
        raise FileNotFoundError(f"No features list found at {FEATURES_PATH}.")
    else:
        model = joblib.load(MODEL_PATH)
        feature_cols = joblib.load(FEATURES_PATH)
        print(f"Model loaded. Features: {feature_cols}")
