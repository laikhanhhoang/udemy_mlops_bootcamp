import mlflow
from mlflow import MlflowClient

mlflow.set_tracking_uri("http://127.0.0.1:5000")

client = MlflowClient()

mvs = client.search_registered_models(
    filter_string="tags.Dataset = 'Red Wine Quality'",
    max_results=10,
    order_by=["name ASC"]
)

for mv in mvs:
    print(f"Name {mv.name}, tags {mv.tags}")