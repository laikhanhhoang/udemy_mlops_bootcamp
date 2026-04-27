# How to run
## 1. Setup venv


```bash
cd ./src
py -3.11 -m venv .venv && .\.venv\Scripts\activate && pip install -r requirements.txt
```

## 2. Run Python script in **`./src/client`**

```bash
cd ./src/client
```

- **src/client/experiments**

    ```bash
    cd experiments # Just to make sure you are on folder experiments


    python exp_elasticnet_gridsearch.py 
        # or python exp_elasticnet_gridsearch.py --nested
    ```

## 3. Setup local MLFlow tracking server in **`src/local_srv_storage`**

```bash
cd ./src/local_srv_storage # Just to make sure you are on folder local_srv_storage


mlflow ui

# or run this command 
    # mlflow server '
    #     --backend-store-uri file:///D:/UDEMY/mlops_bc/mlflow_in_action/mlflow_demo/src/local_srv_storage/mlruns '
    #     --default-artifact-root file:///D:/UDEMY/mlops_bc/mlflow_in_action/mlflow_demo/src/local_srv_storage/# artifacts '
    #     --host 127.0.0.1 '
    #     --port 5000
    # And then go to http://127.0.0.1:5000 on browser.
    # This command is for Windows device. If you use Linux, change "'" into "\".
```