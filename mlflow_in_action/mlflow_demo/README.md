# How to run
## Setup venv


    ```bash
    cd ./src

    py -3.11 -m venv .venv && .\.venv\Scripts\activate
    pip install -r requirements.txt
    ```

## src/client

    ```bash
    python main.py or python main.py --nested
    ```

## src/local_srv_storage

    ```bash

    mlflow ui

    # or
        # mlflow server \
        #     --backend-store-uri file:///D:/UDEMY/mlops_bc/mlflow_in_action/mlflow_demo/src/local_srv_storage/mlruns \
        #     --default-artifact-root file:///D:/UDEMY/mlops_bc/mlflow_in_action/mlflow_demo/src/local_srv_storage/# artifacts \
        #     --host 127.0.0.1 \
        #     --port 5000


    ```



