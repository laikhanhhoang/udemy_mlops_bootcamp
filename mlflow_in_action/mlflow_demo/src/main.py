import os
from pathlib import Path

import warnings
import argparse
import logging
import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.linear_model import ElasticNet
import mlflow
import mlflow.sklearn
from mlflow.models.signature import infer_signature

logging.basicConfig(level=logging.WARN)
logger = logging.getLogger(__name__)

#get arguments from command
parser = argparse.ArgumentParser()
parser.add_argument("--alpha", type=float, required=False, default=0.5)
parser.add_argument("--l1_ratio", type=float, required=False, default=0.5)
args = parser.parse_args()

#evaluation function
def eval_metrics(actual, pred):
    rmse = np.sqrt(mean_squared_error(actual, pred))
    mae = mean_absolute_error(actual, pred)
    r2 = r2_score(actual, pred)
    return rmse, mae, r2


if __name__ == "__main__":
    warnings.filterwarnings("ignore")
    np.random.seed(40)

    # Read the wine-quality csv file from local
    data = pd.read_csv("wine_quality.csv")

    # Split the data into training and test sets. (0.75, 0.25) split.
    train, test = train_test_split(data)

    # The predicted column is "quality" which is a scalar from [3, 9]
    train_x = train.drop(["quality"], axis=1)
    test_x = test.drop(["quality"], axis=1)
    train_y = train[["quality"]]
    test_y = test[["quality"]]

    alpha = args.alpha
    l1_ratio = args.l1_ratio

    # Setup MLFlow experiment

    mlflow.set_tracking_uri("file:///D:/UDEMY/mlops_bc/mlflow_in_action/mlflow_demo/src/mlruns")    
    mlflow.set_experiment("Elasticnet")

    with mlflow.start_run(        
        run_name=f"alpha_{alpha}_l1_{l1_ratio}"
    ):

        lr = ElasticNet(alpha=alpha, l1_ratio=l1_ratio, random_state=42)
        lr.fit(train_x, train_y)

        preds = lr.predict(test_x)

        rmse, mae, r2 = eval_metrics(test_y, preds)

        print(f"ElasticNet model (alpha={alpha}, l1_ratio={l1_ratio}):")
        print(f"  RMSE: {rmse}")
        print(f"  MAE: {mae}")
        print(f"  R2: {r2}")

        mlflow.log_param("alpha", alpha)
        mlflow.log_param("l1_ratio", l1_ratio)
        mlflow.log_metric("rmse", rmse)
        mlflow.log_metric("mae", mae)
        mlflow.log_metric("r2", r2)
        mlflow.set_tag("model", "ElasticNet")
        mlflow.set_tag("dataset", "wine_quality")

        signature = infer_signature(train_x, lr.predict(train_x))
        mlflow.sklearn.log_model(
            lr,
            name="model",
            serialization_format="cloudpickle",
            signature=signature,
            input_example=train_x[:5]
        )

        print(f"Signature of the model: {signature}")