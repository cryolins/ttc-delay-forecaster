from pathlib import Path
from xgboost import XGBRegressor
import numpy as np
from cust_model_utils import load_data, common_preprocess, split_data, compute_metrics, save_metrics, visualize_preds, visualize_key_features

DATA_DIR_PATH = Path(__file__).resolve().parent.parent.parent / "data"
df = common_preprocess(load_data())

# split into datasets
train, val, test, X_train, y_train, X_val, y_val, X_test, y_test = split_data(df)

xgb = XGBRegressor(
    # basic hyperparameters to get something hopefully decent
    n_estimators=800, # high allows for xgb early stopping if needed
    early_stopping_rounds=50,
    max_depth=6,
    learning_rate=0.05,
    gamma=0,

    # to prevent overfitting:
    subsample=0.8,
    colsample_bytree=0.8,
    min_child_weight=3,

    # parameters for running the model
    random_state=42,
    n_jobs=-1,
    verbosity=1
)

print("XGB Fitting Process:")
xgb.fit(
    X_train, y_train,
    eval_set=[(X_val, y_val)],
    verbose=50
)

print(f"Best iteration: {xgb.best_iteration}")

# doing the test
y_pred = xgb.predict(X_test)

metrics = compute_metrics(y_test, y_pred)
save_metrics(metrics, "xgb-default-metrics")
print(metrics)

visualize_key_features(xgb, "xgb-default-features")
visualize_preds(test, y_test, y_pred, "xgb-default-eval")
