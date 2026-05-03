import numpy as np
from pathlib import Path
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from cust_model_utils import load_data, common_preprocess, split_data, compute_metrics, save_metrics, visualize_preds, NUM_FEATURES, CAT_FEATURES

DATA_DIR_PATH = Path(__file__).resolve().parent.parent.parent / "data"
baseline_df = common_preprocess(load_data())

#----------------
# baseline model: linear regressor
#----------------
# building pipeline with one-hot
preprocessor = ColumnTransformer(transformers=[
    ("num", "passthrough", NUM_FEATURES),
    ("cat", OneHotEncoder(handle_unknown="ignore"), CAT_FEATURES)
])
baseline_pipeline = Pipeline(steps=[
    ("preprocessor", preprocessor),
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
