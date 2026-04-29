import mlflow
from mlflow import MlflowClient

mlflow.set_tracking_uri("http://127.0.0.1:5000")

client = MlflowClient()

client.create_model_version(
    name="linear-regression-model",
    source="runs:/e5edb2244a72433f832961516a09b0a7/sklearn_mlflow_pyfunc",
    tags={
        "framework": "sklearn",
        "hyperparameters": "alpha and l1_ratio"
    },
    description="A second linear regression model trained with alpha and l1_ratio prameters."
)