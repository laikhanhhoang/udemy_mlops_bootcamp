import mlflow
from mlflow import MlflowClient

mlflow.set_tracking_uri("http://127.0.0.1:5000")

client = MlflowClient()

client.update_registered_model(
    name="ElasticNet-regression-model",
    description= '''
        The registered model is an ElasticNet model,
         trained on red wine quality dataset to predict the quality of wine.
          Two hyparameters alpha and l1_ratio has been used
    '''
)