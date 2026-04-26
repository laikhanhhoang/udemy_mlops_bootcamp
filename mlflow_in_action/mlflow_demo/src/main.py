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

    if not os.path.exists("data/"):
        os.mkdir("data/")
    train.to_csv("data/train.csv", index=False)
    test.to_csv("data/test.csv", index=False)

    alpha = args.alpha
    l1_ratio = args.l1_ratio

    # =========================================================================
    # MLFLOW TRACKING SETUP
    # =========================================================================
    # Set the tracking URI (Local file path or Remote server URL)
    mlflow.set_tracking_uri("file:///D:/UDEMY/mlops_bc/mlflow_in_action/mlflow_demo/src/mlruns")    
    
    # Define the experiment name to group related runs
    mlflow.set_experiment("Elasticnet")
    # Alternative: exp = mlflow.set_experiment("Elasticnet")
    # Then use: with mlflow.start_run(experiment_id=exp.experiment_id):

    # Start an MLflow run to track the training process
    with mlflow.start_run(run_name=f"alpha_{alpha}_l1_{l1_ratio}"):

        # --- Model Training ---
        lr = ElasticNet(alpha=alpha, l1_ratio=l1_ratio, random_state=42)
        lr.fit(train_x, train_y)

        # --- Model Evaluation ---
        preds = lr.predict(test_x)
        rmse, mae, r2 = eval_metrics(test_y, preds)

        print(f"ElasticNet model (alpha={alpha}, l1_ratio={l1_ratio}):")
        print(f"  RMSE: {rmse} | MAE: {mae} | R2: {r2}")

        # =====================================================================
        # 1. LOG PARAMETERS (Input Configurations/Hyperparameters)
        # =====================================================================
        mlflow.log_param("alpha", alpha)
        mlflow.log_param("l1_ratio", l1_ratio)
        
        # Batch logging alternative: mlflow.log_params({"alpha": alpha, "l1_ratio": l1_ratio})

        # =====================================================================
        # 2. LOG METRICS (Output Performance Results)
        # =====================================================================
        mlflow.log_metric("rmse", rmse)
        mlflow.log_metric("mae", mae)
        mlflow.log_metric("r2", r2)
        
        # Batch logging alternative: mlflow.log_metrics({"rmse": rmse, "mae": mae, "r2": r2})

        # =====================================================================
        # 3. LOG TAGS (Metadata for Search and Filtering)
        # =====================================================================
        mlflow.set_tag("model", "ElasticNet")
        mlflow.set_tag("dataset", "wine_quality")

        # Batch tagging alternative: mlflow.set_tags({"model": "ElasticNet", "dataset": "wine_quality"})
        
        # =====================================================================
        # 4. LOG MODEL (Save Model Object & Metadata)
        # =====================================================================
        # Infer the model signature (input and output schema)
        signature = infer_signature(train_x, lr.predict(train_x))
        
        mlflow.sklearn.log_model(
            sk_model=lr,
            artifact_path="model", # Destination folder name within artifacts
            serialization_format="cloudpickle",
            signature=signature,
            input_example=train_x[:5]
        )
        print(f"Signature of the model: {signature}")

        # =====================================================================
        # 5. LOG ARTIFACTS (External Files and Directories)
        # =====================================================================
        # Log a single file
        mlflow.log_artifact("wine_quality.csv")

        # Log an entire directory to a specific path in MLflow
        mlflow.log_artifacts("data/", artifact_path="data_used")

        # =====================================================================
        # 6. RUN RETRIEVAL (Query current run information)
        # =====================================================================
        # Get information about the currently active run
        run = mlflow.active_run()
        print(f"Run ID: {run.info.run_id}")
        print(f"Run name: {run.info.run_name}")
        print(f"Artifact URI: {mlflow.get_artifact_uri()}")

        # Or you can access run's info after ending the run:
            # mlflow.end_run() 
            # run = mlflow.last_active_run()