import numpy as np
from pathlib import Path
from xgboost import XGBRegressor
from cust_model_utils import load_data, common_preprocess, split_data, compute_metrics, save_metrics, visualize_preds, visualize_key_features, ohe_preprocessor
from sklearn.model_selection import RandomizedSearchCV, TimeSeriesSplit
import joblib

DATA_DIR_PATH = Path(__file__).resolve().parent.parent.parent / "data"
df = common_preprocess(load_data())
train, val, test, X_train, y_train, X_val, y_val, X_test, y_test = split_data(df)

feature_cols = X_train.columns.to_list()
print(feature_cols)
joblib.dump(feature_cols, "feature_cols.pkl")

param_grid = {
    "n_estimators": [200, 300, 400, 500],
    "max_depth": [3, 5, 7],
    "learning_rate": [0.03, 0.05, 0.075, 0.1],
    "subsample": [0.6, 0.7, 0.8, 0.9],
    "colsample_bytree": [0.6, 0.7, 0.8, 0.9],
    "min_child_weight": [1, 3, 5, 7],
    "gamma":  [0, 0.1, 0.2, 0.5],
    "max_cat_to_onehot": [8, 16]
}

tscv = TimeSeriesSplit(n_splits=5) # time series cross validation

search = RandomizedSearchCV(
    estimator=XGBRegressor(
        random_state=42, 
        enable_categorical=True
    ),
    param_distributions=param_grid,
    n_iter=150,
    scoring="neg_mean_absolute_error",
    cv=tscv,
    verbose=2,
    random_state=42,
    n_jobs=-1
)

search.fit(X_train, y_train, verbose=0)
print("Best parameters:")
print(search.best_params_.items())
print(search.best_score_)
del search.best_params_["n_estimators"]

# retraining with best
best_xgb = XGBRegressor(
    **search.best_params_, # use those tuned params
    n_estimators=1000,
    early_stopping_rounds=50,
    random_state=42, 
    n_jobs=-1, 
    verbosity=1,
    enable_categorical=True
)

best_xgb.fit(
    X_train, y_train,
    eval_set=[(X_val, y_val)],
    verbose=50
)

print(f"Best iteration: {best_xgb.best_iteration}")

# doing the test
y_pred = best_xgb.predict(X_test)

metrics = compute_metrics(y_test, y_pred)
save_metrics(metrics, "xgb-tuned-metrics")
print(metrics)

visualize_key_features(best_xgb, "xgb-tuned-features")
visualize_preds(test, y_test, y_pred, "xgb-tuned-eval")

joblib.dump(best_xgb, "delay_model_v3-1_1h.pkl")
