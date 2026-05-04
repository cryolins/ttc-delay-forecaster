import numpy as np
from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from cust_model_utils import load_data, common_preprocess, split_data, compute_metrics, save_metrics, visualize_preds, ohe_preprocessor

DATA_DIR_PATH = Path(__file__).resolve().parent.parent.parent / "data"
baseline_df = common_preprocess(load_data())

#----------------
# baseline model: linear regressor
#----------------
# building pipeline with one-hot
baseline_pipeline = Pipeline(steps=[
    ("preprocessor", ohe_preprocessor),
    ("model", LinearRegression())
])

# split into datasets based on time (test on later dataset)
train, test, X_train, y_train, X_test, y_test = split_data(baseline_df, False)

# run model
baseline_pipeline.fit(X_train, y_train)
y_pred = baseline_pipeline.predict(X_test)

metrics = compute_metrics(y_test, y_pred)
save_metrics(metrics, "baseline-metrics")
print(metrics)

visualize_preds(test, y_test, y_pred, "baseline-eval")
