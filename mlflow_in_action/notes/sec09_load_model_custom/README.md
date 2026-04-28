# Sec09: Handling Customized Models

Section này hướng dẫn cách quản lí một custom model với MLFlow qua **`mlflow.pyfunc`**, cụ thể làm việc với file [exp_sklearn_pyfunc.py](/mlflow_in_action/mlflow_demo/src/client/experiments/exp_sklearn_pyfunc.py).

| Lệnh | Công dụng | Tham số truyền vào | Đặc điểm lưu ý |
| :--- | :--- | :--- | :--- |
| **[mlflow.pyfunc.log_model](https://mlflow.org/docs/latest/api_reference/python_api/mlflow.pyfunc.html#mlflow.pyfunc.log_model)** | Đóng gói và lưu trữ một mô hình Python tùy chỉnh (hoặc mô hình từ framework khác dưới dạng pyfunc) vào MLflow Tracking server. | <ul><li>**artifact_path**: `string`<br>Ví dụ: `"my_model_folder"`</li><li>**python_model**: `PythonModel instance`<br>Ví dụ: `MyModelClass()`</li><li>**artifacts**: `dict`<br>Ví dụ: `{"config": "config.yaml"}`</li><li>**conda_env**: `string` hoặc `dict`<br>Ví dụ: `"env.yaml"`</li><li>**code_paths**: `list[string]`<br>Ví dụ: `["utils.py", "preprocessing.py"]`</li><li>**registered_model_name**: `string`<br>Ví dụ: `"Production_Model"`</li><li>**signature**: `ModelSignature`<br>Ví dụ: `infer_signature(X, y)`</li><li>**input_example**: `DataFrame/ndarray/dict/...`<br>Ví dụ: `X_train[:3]`</li><li>**pip_requirements**: `list/str`<br>Ví dụ: `["numpy", "-r requirements.txt"]` hoặc `"src/requirements.txt"`</li><li>**extra_pip_requirements**: `list`<br>Ví dụ: `["boto3"]`</li><li>**metadata**: `dict`<br>Ví dụ: `{"department": "AI-Lab"}`</li></ul> | **Pyfunc** là định dạng "wrapper" vạn năng. Nó cho phép bạn triển khai mô hình lên bất kỳ môi trường nào (Docker, Spark, K8s) mà không cần cài đặt lại code framework gốc (như PyTorch hay Sklearn) nếu đã cấu hình đúng môi trường. |





