from sklearn.ensemble import RandomForestRegressor
from cust_model_utils import load_data, common_preprocess, split_data, compute_metrics, save_metrics, visualize_preds, visualize_key_features

df = common_preprocess(load_data())
train, test, X_train, y_train, X_test, y_test = split_data(df, False)

print("starting regressor")
forest = RandomForestRegressor(
    n_estimators=100,
    criterion="absolute_error",
    max_depth=10,
    random_state=42,
    n_jobs=-1
)
forest.fit(X_train, y_train)
y_train_pred = forest.predict(X_train)
y_pred = forest.predict(X_test)

print("computing metrics")
train_metrics = compute_metrics(y_train, y_train_pred)
print(train_metrics)
metrics = compute_metrics(y_test, y_pred)
save_metrics(metrics, "forest-metrics")
print(metrics)

visualize_key_features(forest, "forest-features")
visualize_preds(test, y_test, y_pred, "forest-eval")
