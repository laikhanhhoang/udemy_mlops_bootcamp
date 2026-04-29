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

# ==================================================================
# CUSTOM EVALUATION FUNCTIONS
# ==================================================================

def squared_diff_plus_one(eval_df, _builtin_metrics):
    """
    Calculates the sum of squared differences between predictions 
    and targets, shifted by one.
    """
    return np.sum(np.abs(eval_df["prediction"] - eval_df["target"] + 1) ** 2)

def sum_on_target_divided_by_two(eval_df, _builtin_metrics):
    """
    Returns half of the built-in 'sum_on_target' metric.
    """
    return _builtin_metrics["sum_on_target"] / 2

def prediction_target_scatter(eval_df, _builtin_metrics, artifacts_dir):
    """
    Generates a scatter plot of Predictions vs. Targets and saves it as an artifact.
    """
    plt.figure(figsize=(10, 6))
    plt.scatter(eval_df["prediction"], eval_df["target"], alpha=0.5)
    plt.xlabel("Targets")
    plt.ylabel("Predictions")
    plt.title("Targets vs. Predictions")
    
    # Save plot to the temporary artifacts directory provided by MLflow
    plot_path = os.path.join(artifacts_dir, "example_scatter_plot.png")
    plt.savefig(plot_path)
    plt.close() 
    return {"example_scatter_plot_artifact": plot_path}

# ==================================================================
# MAIN EXECUTION
# ==================================================================

if __name__ == "__main__":
    warnings.filterwarnings("ignore")
    np.random.seed(40)

    # CLI Arguments Setup
    parser = argparse.ArgumentParser(description="Evaluate MLflow models against a baseline.")
    parser.add_argument("--model_run_id", type=str, required=True, help="Run ID of the candidate model")
    parser.add_argument("--baseline_run_id", type=str, required=False, default=None, help="Run ID of the baseline model")
    args = parser.parse_args()

    # MLflow Tracking Configuration
    mlflow.set_tracking_uri("file:///D:/UDEMY/mlops_bc/mlflow_in_action/mlflow_demo/src/local_srv_storage/mlruns")    

    # Construct MLflow URIs (Format: runs:/<run_id>/<model_path>)
    model_uri = f"runs:/{args.model_run_id}/model"
    baseline_uri = f"runs:/{args.baseline_run_id}/model" if args.baseline_run_id else None

    # Load Test Dataset
    try:
        data = pd.read_csv("../experiments/data/test.csv")
    except FileNotFoundError:
        logger.error("Test data file not found at the specified path.")
        exit(1)

    # Wrap custom logic into MLflow Metric objects
    squared_diff_plus_one_metric = mlflow.models.make_metric(
        eval_fn=squared_diff_plus_one,
        greater_is_better=False,
        name="squared diff plus one"
    )

    sum_on_target_divided_by_two_metric = mlflow.models.make_metric(
        eval_fn=sum_on_target_divided_by_two,
        greater_is_better=True,
        name="sum on target divided by two"
    )

    # Define Model Validation Thresholds (Pass/Fail criteria)
    thresholds = {
        "mean_squared_error": mlflow.models.MetricThreshold(
            threshold=0.6,             # Absolute max limit
            min_absolute_change=0.1,   # Must improve by at least 0.1 vs baseline
            min_relative_change=0.05,  # Must improve by at least 5% vs baseline
            greater_is_better=False    # For MSE, lower values are better
        )
    }

    # Execute Evaluation within a dedicated MLflow Run
    with mlflow.start_run(run_id = args.model_run_id) as run:
        evaluate_results = mlflow.evaluate(
            model               = model_uri,
            data                = data,           
            targets             = "quality",
            model_type          = "regressor",
            evaluators          = ["default"],
            extra_metrics       = [
                squared_diff_plus_one_metric,
                sum_on_target_divided_by_two_metric
            ],
            custom_artifacts    = [prediction_target_scatter], 
            validation_thresholds   = thresholds,
            baseline_model          = baseline_uri
        )
        
    print("-" * 40)
    print("Evaluation Completed Successfully!")
    print(f"Candidate Model: {model_uri}")
    print(f"Baseline Model:  {baseline_uri if baseline_uri else 'None'}")
    print(f"Results Logged to Run ID: {run.info.run_id}")
    print("-" * 40)