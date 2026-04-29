import mlflow
from mlflow import MlflowClient
from mlflow.entities import ViewType

if __name__ == "__main__":
    mlflow.set_tracking_uri("http://127.0.0.1:5000")
    # or mlflow.set_tracking_uri("file:///D:/UDEMY/mlops_bc/mlflow_in_action/mlflow_demo/src/local_srv_storage/mlruns")    


    client = MlflowClient()

    experiments = client.search_experiments(view_type=ViewType.ALL,
                                            filter_string="name = 'ElasticNet_Pyfunc'",
                                            order_by=["experiment_id ASC"]
                                            )

    for exp in experiments:
        print(f"Experiment Name: {exp.name}, Experiment ID: {exp.experiment_id}")
