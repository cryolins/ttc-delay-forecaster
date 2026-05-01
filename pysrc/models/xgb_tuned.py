from pathlib import Path
from xgboost import XGBRegressor
from cust_model_utils import load_data, common_preprocess, split_data, compute_metrics, save_metrics, visualize_preds, visualize_key_features
from sklearn.model_selection import RandomizedSearchCV, TimeSeriesSplit

DATA_DIR_PATH = Path(__file__).resolve().parent.parent.parent / "data"
df = common_preprocess(load_data())
train, val, test, X_train, y_train, X_val, y_val, X_test, y_test = split_data(df)

param_grid = {
    "n_estimators": [70, 100, 200, 300, 500],
    "max_depth": [3, 4, 5, 6, 7],
    "learning_rate": [0.01, 0.03, 0.05, 0.1, 0.2, 0.3],
    "subsample": [0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
    "colsample_bytree": [0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
    "min_child_weight": [1, 3, 5, 7],
    "gamma":  [0, 0.1, 0.2, 0.5]
}

tscv = TimeSeriesSplit(n_splits=5) # time series cross validation

search = RandomizedSearchCV(
    estimator=XGBRegressor(
        random_state=42, 
        n_jobs=-1, 
    ),
    param_distributions=param_grid,
    n_iter=100,
    scoring="neg_mean_absolute_error",
    cv=tscv,
    verbose=3,
    random_state=42,
    n_jobs=-1
)

search.fit(X_train, y_train)
print("Best parameters:")
print(search.best_params_.items())
print(search.best_score_)
best_xgb = search.best_estimator_

# doing the test
y_pred = best_xgb.predict(X_test)

metrics = compute_metrics(y_test, y_pred)
save_metrics(metrics, "xgb-tuned-metrics")
print(metrics)

visualize_key_features(best_xgb, "xgb-tuned-features")
visualize_preds(test, y_test, y_pred, "xgb-tuned-eval")
