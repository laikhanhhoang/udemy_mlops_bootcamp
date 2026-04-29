import os
import warnings
import logging
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import mlflow

# Configure Logging: Set level to WARN to filter out INFO/DEBUG noise
logging.basicConfig(level=logging.WARN)
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    warnings.filterwarnings("ignore")
    np.random.seed(40)

    # CLI Arguments Setup
    parser = argparse.ArgumentParser(description="Evaluate MLflow models against a baseline.")
    parser.add_argument("--run_id", type=str, required=True, help="Run ID of the candidate model")
    parser.add_argument("--model_name", type=str, required=True, help="Name for the registered model")
    args = parser.parse_args()

    # Set MLflow Tracking URI to the local file-based storage
    mlflow.set_tracking_uri("file:///D:/UDEMY/mlops_bc/mlflow_in_action/mlflow_demo/src/local_srv_storage/mlruns")    

    # Register the model in MLflow Model Registry
    model_name = args.model_name
    mlflow.register_model(model_uri=f"runs:/{args.run_id}/model", name=model_name)