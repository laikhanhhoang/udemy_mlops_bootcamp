import mlflow
from mlflow import MlflowClient

mlflow.set_tracking_uri("http://127.0.0.1:5000")

client = MlflowClient()

client.update_model_version(
    name="linear-regression-model",
    version="1",
    description="First model trained on red wine quality dataset"
)