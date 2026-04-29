import mlflow
from mlflow import MlflowClient

mlflow.set_tracking_uri("http://127.0.0.1:5000")

client = MlflowClient()

client.create_registered_model(
    name="linear-regression-model",
    tags={
        "framework": "Pytorch",
        "model": "Transformer",
    },
    description="Attention is all you need",
)

