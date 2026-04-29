import mlflow
from mlflow import MlflowClient

mlflow.set_tracking_uri("http://127.0.0.1:5000")

client = MlflowClient()

client.set_model_version_tag(
    name="linear-regression-model",
    version="1",
    key="framework",
    value="sklearn",
)

client.set_model_version_tag(
    name="linear-regression-model",
    version="1",
    key="hyperparameters",
    value="alpha and l1_ratio",
)