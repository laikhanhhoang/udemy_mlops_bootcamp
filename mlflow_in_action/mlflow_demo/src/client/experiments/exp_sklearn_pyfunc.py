import os
from pathlib import Path
from contextlib import nullcontext

import warnings, argparse, logging, joblib
import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.linear_model import ElasticNet
import mlflow
import mlflow.sklearn
from mlflow.models.signature import infer_signature


# =====================================================================
# !!!!

# THIS EXPERIMENT ASSUMES THAT SKLEARN IS NOT SUPPORTED BY THE CURRENT MLFLOW VERSION, 
# THEREFORE WE WILL LOG THE MODEL USING mlflow.pyfunc (Generic Python Model) INSTEAD OF mlflow.sklearn

# Most changes will be in the "4. LOG MODEL (Save Model Object & Metadata)" (you can search it) section, 
# where we will define a custom PythonModel wrapper to load and use the sklearn model, and log it using mlflow.pyfunc.log_model() instead of mlflow.sklearn.log_model()

# !!!
# =====================================================================

logging.basicConfig(level=logging.WARN)
logger = logging.getLogger(__name__)

#get arguments from command
parser = argparse.ArgumentParser()
parser.add_argument("--exp_name", type=str, required=False, default="Elasticnet")
parser.add_argument("--nested", action="store_true")
parser.add_argument("--alpha", type=float, required=False, default=0.5)
parser.add_argument("--l1_ratio", type=float, required=False, default=0.5)
parser.add_argument("--alphas", nargs="*", type=float, required=False, default=[0.1, 0.5])
parser.add_argument("--l1_ratios", nargs="*", type=float, required=False, default=[0.2, 0.8])
args = parser.parse_args()

#evaluation function
def eval_metrics(actual, pred):
    rmse = np.sqrt(mean_squared_error(actual, pred))
    mae = mean_absolute_error(actual, pred)
    r2 = r2_score(actual, pred)
    return rmse, mae, r2


def train_and_log_mlflow(alpha_list, l1_list, train_x, train_y, test_x, test_y, is_nested=False):
    p_name = "GridSearch_ElasticNet" if is_nested else f"alpha_{alpha_list[0]}_l1_{l1_list[0]}"
    with mlflow.start_run(run_name=p_name) as parent_run:
            # if nested mode, we will create a nested run for each hyperparameter combination, otherwise we will log everything in the parent run
            for alpha in alpha_list:
                for l1_ratio in l1_list:
                    # Chỉ tạo nested run nếu is_nested=True, ngược lại chạy trực tiếp trong parent_run
                    run_ctx = mlflow.start_run(run_name=f"a_{alpha}_l1_{l1_ratio}", nested=True) if is_nested else nullcontext()

                    with run_ctx:

                        # --- Model Training ---
                        lr = ElasticNet(alpha=alpha, l1_ratio=l1_ratio, random_state=42)
                        lr.fit(train_x, train_y)

                        # --- Model Evaluation ---
                        preds = lr.predict(test_x)
                        rmse, mae, r2 = eval_metrics(test_y, preds)

                        print(f"ElasticNet model (alpha={alpha}, l1_ratio={l1_ratio}):")
                        print(f"  RMSE: {rmse} | MAE: {mae} | R2: {r2}")

                        # --- LOGGING TO MLFLOW ---
                        # 1. LOG PARAMETERS (Input Configurations/Hyperparameters)
                        mlflow.log_param("alpha", alpha)
                        mlflow.log_param("l1_ratio", l1_ratio)
                        # Batch logging alternative: mlflow.log_params({"alpha": alpha, "l1_ratio": l1_ratio})

                        # 2. LOG METRICS (Output Performance Results)
                        mlflow.log_metric("rmse", rmse)
                        mlflow.log_metric("mae", mae)
                        mlflow.log_metric("r2", r2)
                        # Batch logging alternative: mlflow.log_metrics({"rmse": rmse, "mae": mae, "r2": r2})

                        # 3. LOG TAGS (Metadata for Search and Filtering)
                        mlflow.set_tag("model", "ElasticNet")
                        mlflow.set_tag("dataset", "wine_quality")
                        # Batch tagging alternative: mlflow.set_tags({"model": "ElasticNet", "dataset": "wine_quality"})
                        
                        # 4. LOG MODEL (Save Model Object & Metadata)
                        artifact_path = "model_pyfunc" # Define the artifact path within the run's artifact storage where the model will be saved

                        
                        class SklearnWrapper(mlflow.pyfunc.PythonModel): # Define a custom PythonModel wrapper to load and use the sklearn model
                            def load_context(self, context):
                                self.sklearn_model = joblib.load(context.artifacts["sklearn_model"])

                            def predict(self, context, model_input):
                                return self.sklearn_model.predict(model_input.values)

                        sklearn_model_path = "weights/elasticnet_sklearn.pkl" # Save the sklearn model to a file and prepare artifacts for logging
                        folder = os.path.dirname(sklearn_model_path) # Ensure the directory exists before saving the model
                        if not os.path.exists(folder):
                            os.makedirs(folder)
                        joblib.dump(lr, sklearn_model_path)

                        data_dir = "data/"
                        artifacts = {
                            "sklearn_model" : sklearn_model_path,
                            "data" : data_dir
                        }

                        code_paths = ["exp_sklearn_pyfunc.py"]  # Defile specify code files/folder to be logged with the model
                        pip_requirements = r"D:/UDEMY/mlops_bc/mlflow_in_action/mlflow_demo/src/requirements.txt"   # Define pip requirements file to specify dependencies needed to run the model (alternative: conda environment file)
                        signature = infer_signature(train_x, lr.predict(train_x))   # Define model signature (input and output schema) for better model serving and deployment support (optional but recommended)
                        input_example = train_x.head(5) # Define an input example for the model (optional but recommended for better model understanding and testing in deployment)
                        metadata = {"rmse": float(rmse), "mae": float(mae), "r2": float(r2)}    # Define custom metadata to be logged with the model (optional, can include any relevant information about the model or training process)

                        # Log the model using mlflow.pyfunc.log_model() with the defined wrapper, artifacts, code paths, dependencies, signature, input example, and metadata
                        mlflow.pyfunc.log_model(
                            artifact_path=artifact_path,
                            python_model=SklearnWrapper(),
                            artifacts=artifacts,
                            code_path=code_paths,
                            pip_requirements=pip_requirements,
                            signature=signature,
                            input_example=input_example,
                            metadata=metadata
                        )

                        # 5. LOG ARTIFACTS (External Files and Directories)
                        mlflow.log_artifact("wine_quality.csv") # Log a single file

                        mlflow.log_artifacts("data/", artifact_path="data_used") # Log an entire directory to a specific path in MLflow

                        # 6. RUN RETRIEVAL (Query current run information)
                        # Get information about the currently active run
                        run = mlflow.active_run()
                        print(f"Run ID: {run.info.run_id}")
                        print(f"Run name: {run.info.run_name}")
                        print(f"Artifact URI: {mlflow.get_artifact_uri()}")
                        # Or you can access run's info after ending the run:
                            # mlflow.end_run() 
                            # run = mlflow.last_active_run()



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


    if args.nested:
        alphas_to_run = args.alphas
        l1_to_run = args.l1_ratios
        is_nested_mode = True
    else:
        alphas_to_run = [args.alpha]
        l1_to_run = [args.l1_ratio]
        is_nested_mode = False
        

    # =========================================================================
    # MLFLOW TRACKING SETUP
    # =========================================================================
    # Set the tracking URI (Local file path or Remote server URL)
    mlflow.set_tracking_uri("file:///D:/UDEMY/mlops_bc/mlflow_in_action/mlflow_demo/src/local_srv_storage/mlruns")    
    
    # Define the experiment name to group related runs
    experiment_name = args.exp_name
    artifact_location = "file:///D:/UDEMY/mlops_bc/mlflow_in_action/mlflow_demo/src/local_srv_storage/myartifacts" # Optional: specify where to store artifacts for this experiment

    if mlflow.get_experiment_by_name(experiment_name) is None:
        mlflow.create_experiment(experiment_name, artifact_location=artifact_location)
    
    # Activate the experiment so that all runs will be logged under this experiment
    mlflow.set_experiment(experiment_name)

    # Start an MLflow run to track the training process
    train_and_log_mlflow(
        alphas_to_run, 
        l1_to_run, 
        train_x, train_y, test_x, test_y, 
        is_nested=is_nested_mode
    )
    
