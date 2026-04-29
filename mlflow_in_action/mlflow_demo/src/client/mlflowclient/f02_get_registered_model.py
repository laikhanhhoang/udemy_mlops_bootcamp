import mlflow
from mlflow import MlflowClient

mlflow.set_tracking_uri("http://127.0.0.1:5000")

client = MlflowClient()

mv = client.get_registered_model(
    name="ElasticNet-regression-model"
)

print("Name", mv.name)
print("Description", mv.description)
print("Tags", mv.tags)