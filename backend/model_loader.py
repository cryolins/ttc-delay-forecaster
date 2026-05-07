import joblib
from pathlib import Path
from backend_utils import CAT_FEATURES

MODEL_PATH = Path("./model/delay_model_V3-1.pkl")
FEATURES_PATH = Path("./model/feature_cols.pkl")

# set up global exports
model = None
feature_cols = None
encoders: dict = {}

# function to load in these variables
def load_model():
    global model, feature_cols, encoders
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"No model found at {MODEL_PATH}.")
    elif not FEATURES_PATH.exists():
        raise FileNotFoundError(f"No features list found at {FEATURES_PATH}.")
    else:
        model = joblib.load(MODEL_PATH)
        feature_cols = joblib.load(FEATURES_PATH)
        local_encoders = {}
        for cat_feat in CAT_FEATURES:
            local_encoders[cat_feat] = joblib.load(Path(f"./model/{cat_feat}_label_enc.pkl"))
        encoders = local_encoders
        print(f"Model loaded. Features: {feature_cols}")
