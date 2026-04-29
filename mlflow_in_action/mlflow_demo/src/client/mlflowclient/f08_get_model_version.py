import mlflow
from mlflow import MlflowClient

mlflow.set_tracking_uri("http://127.0.0.1:5000")

client = MlflowClient()

mv = client.get_model_version(
    name="linear-regression-model",
    version="2"
)

print("Name:", mv.name)
print("Version:", mv.version)
print("Tags:", mv.tags)
print("Description:", mv.description)
print("Stage:", mv.current_stage)

