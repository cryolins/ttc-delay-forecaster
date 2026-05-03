import numpy as np
from pathlib import Path
from xgboost import XGBRegressor
from cust_model_utils import load_data, common_preprocess, split_data, compute_metrics, save_metrics, visualize_preds, visualize_key_features
from sklearn.model_selection import RandomizedSearchCV, TimeSeriesSplit
import joblib

DATA_DIR_PATH = Path(__file__).resolve().parent.parent.parent / "data"
df = common_preprocess(load_data())
train, val, test, X_train, y_train, X_val, y_val, X_test, y_test = split_data(df)

y_train_log= np.log1p(y_train)
y_val_log= np.log1p(y_val)

param_grid = {
    "max_depth": [3, 4, 5, 6, 7],
    "learning_rate": [0.03, 0.05, 0.075, 0.1],
    "subsample": [0.6, 0.7, 0.8, 0.9],
    "colsample_bytree": [0.6, 0.7, 0.8, 0.9],
    "min_child_weight": [1, 3, 5, 7],
    "gamma":  [0, 0.1, 0.2, 0.5]
}

tscv = TimeSeriesSplit(n_splits=5) # time series cross validation

search = RandomizedSearchCV(
    estimator=XGBRegressor(
        n_estimators=800,
        early_stopping_rounds=50,
        random_state=42, 
        n_jobs=-1, 
    ),
    param_distributions=param_grid,
    n_iter=150,
    scoring="neg_mean_absolute_error",
    cv=tscv,
    verbose=3,
    random_state=42,
    n_jobs=-1
)

search.fit(X_train, y_train_log, eval_set=[(X_val, y_val_log)], verbose=0)
print("Best parameters:")
print(search.best_params_.items())
print(search.best_score_)

# retraining with best
best_xgb = XGBRegressor(
    **search.best_params_, # use those tuned params
    n_estimators=800,
    early_stopping_rounds=50,
    random_state=42, 
    n_jobs=-1, 
    verbosity=1
)

best_xgb.fit(
    X_train, y_train_log,
    eval_set=[(X_val, y_val_log)],
    verbose=50
)

print(f"Best iteration: {best_xgb.best_iteration}")

# doing the test
y_pred_log = best_xgb.predict(X_test)
y_pred = np.expm1(y_pred_log)


metrics = compute_metrics(y_test, y_pred)
save_metrics(metrics, "xgb-tuned-metrics")
print(metrics)

visualize_key_features(best_xgb, "xgb-tuned-features")
visualize_preds(test, y_test, y_pred, "xgb-tuned-eval")

joblib.dump(best_xgb, "delay_model_v2.pkl")
