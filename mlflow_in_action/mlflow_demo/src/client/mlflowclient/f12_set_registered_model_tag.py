import mlflow
from mlflow import MlflowClient

mlflow.set_tracking_uri("http://127.0.0.1:5000")

client = MlflowClient()

client.set_registered_model_tag(
    name="ElasticNet-regression-model",
    key="Dataset",
    value="Red Wine Quality"
)