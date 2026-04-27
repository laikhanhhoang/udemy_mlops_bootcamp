# Sec07: MLFlow Tracking Server

## 1. Tracking Server Theory

MLflow Tracking Server đóng vai trò là trung tâm quản lý các thực nghiệm (experiments). Cấu trúc của nó tập trung vào hai mảng chính: Lưu trữ (Storage) và Giao tiếp (Communication).

### 1.1. Thành phần Lưu trữ (Storage Components)
Hệ thống chia tách dữ liệu thành hai loại dựa trên đặc tính của chúng:

* **Backend Store (Lưu trữ Metadata):**
    * **Nhiệm vụ:** Lưu các dữ liệu nhẹ, có cấu trúc như: Parameters, Metrics, Tags, Notes và Run Status.
    * **Loại hình:**
        * *File-based:* Lưu cục bộ (mặc định tại `./mlruns`).
        * *Database-backed:* Sử dụng các CSDL quan hệ (PostgreSQL, MySQL, SQLite) thông qua SQLAlchemy. Đây là lựa chọn tối ưu cho môi trường làm việc nhóm (Production).

* **Artifact Store (Lưu trữ Tệp tin):**
    * **Nhiệm vụ:** Lưu các dữ liệu nặng, không cấu trúc như: Model weights (v.v. `.pth`, `.onnx`), hình ảnh biểu đồ, file log hoặc bộ dữ liệu (datasets).
    * **Loại hình:** Hệ thống tệp cục bộ hoặc các dịch vụ Cloud Storage (Amazon S3, Azure Blob Storage, GCS).

### 1.2. Giao tiếp và Mạng (Network & Communication)
Cách thức các thành phần trong hệ sinh thái MLOps tương tác với nhau:


| Thành phần | Cơ chế | Đặc điểm & Vai trò | Trường hợp sử dụng |
| :--- | :--- | :--- | :--- |
| **Giao thức chính** | **REST API (HTTP)** | Ngôn ngữ giao tiếp mặc định. Mọi thao tác log metric, param hay truy vấn đều thực hiện qua các Endpoint chuẩn. | Dùng cho tất cả các **MLflow Client** (Python, R, Java). |
| **Bảo mật & Luồng dữ liệu** | **Artifact Proxy** | **Server đóng vai trò trung gian**. Client gửi file qua Server thay vì đẩy trực tiếp lên Cloud Storage (S3, Azure). | Khi cần bảo mật Credentials của Cloud hoặc **giới hạn quyền truy cập trực tiếp từ máy Client**. |
| **Tối ưu hóa (Lớp Serving)** | **gRPC** | Không dùng cho Tracking. Giao thức nhị phân hiệu suất cao, giúp truyền tải dữ liệu dự đoán nhanh hơn. | Thường xuất hiện ở các công cụ phục vụ model như TensorFlow Serving hoặc TorchServe. |
| **Kiểm soát truy cập** | **Reverse Proxy** | Thường dùng NGINX hoặc Apache đứng trước MLflow Server để điều phối traffic. | Khi cần **triển khai HTTPS** hoặc **thêm lớp xác thực người dùng** (Authentication/Basic Auth). |

### 1.3. Mô hình hoạt động (Workflow)
1. **Client** gọi hàm `mlflow.log_*`.
2. Yêu cầu được gửi qua **REST API** đến Server.
3. **Server Logic** điều hướng:
    * Metadata đẩy vào **Backend Store** (SQL DB).
    * Artifacts đẩy vào **Artifact Store** (S3/Azure Blob/Local).


## 2. Tracking server patterns
### 2.1. Local

- Trong môi trường local, MLflow **có 3 mô hình triển khai chủ yếu** dựa trên cách lưu trữ Metadata (params, metrics, tags) và Artifacts (model, files):
    - MLFLow on localhost dùng FileStore
    - MLFLow on localhost dùng SQLite
    - Host local MLFlow Tracking Server

- **So sánh các pattern**:

    | Tiêu chí | FileStore (Mặc định) | SQLite (Database) | Local Tracking Server |
    | :--- | :--- | :--- | :--- |
    | **Lưu Metadata** | Các file `meta.yaml` và text trong folder `mlruns` | File database duy nhất `mlflow.db` | Server quản lý (thường lưu vào DB) |
    | **Lưu Artifacts** | Thư mục local (mặc định trong `mlruns`) | Thư mục local | Thư mục local (hoặc S3/GCS/Azure) |
    | **Ưu điểm** | Đơn giản nhất, không cần cài đặt thêm. | Truy vấn nhanh, UI load mượt, dữ liệu tập trung. | Sát với môi trường thực tế tại doanh nghiệp. |
    | **Nhược điểm** | Quá nhiều file nhỏ, khó quản lý khi số lượng Run lớn. | Cần cài thêm `sqlalchemy`. | Phải duy trì một tiến trình server chạy ngầm. |


- **Code setup mẫu**:

    - <details>

        <summary><b>Pattern 1 - MLflow localhost dùng FileStore</b></summary>

        <br>

        Đây là cách tiếp cận "zero-config", phù hợp khi mới bắt đầu để hiểu cấu trúc thư mục của MLflow.

        ```python
        import mlflow

        # Thiết lập Tracking URI trỏ đến một thư mục local
        # MLflow sẽ dùng FileStore để lưu Metadata dưới dạng YAML
        mlflow.set_tracking_uri("file:///D:/UDEMY/mlops_bc/mlflow_in_action/mlflow_demo/src/mlruns")    
        
        # Thiết lập URI trỏ đến thư mục lưu artifact (artifacts,model,...)
        experiment_name = args.exp_name
        artifact_location = "file:///D:/UDEMY/mlops_bc/mlflow_in_action/mlflow_demo/src/artifacts"

        if mlflow.get_experiment_by_name(experiment_name) is None:
            mlflow.create_experiment(experiment_name, artifact_location=artifact_location)
        
        # Activate experiment vì create_experiment chỉ tạo đối tượng chứ chưa setup MLFlow cho process này
        mlflow.set_experiment(experiment_name)

        with mlflow.start_run():
            mlflow.log_param("alpha", 0.5)
            mlflow.log_metric("rmse", 0.8)
            # Artifacts sẽ được lưu mặc định trong folder mlruns/<exp_id>/<run_id>/artifacts
        ```
        </details>

    - <details>

        <summary><b>Pattern 2 - MLflow localhost dùng SQLite</b></summary>

        <br>       

        Sử dụng SQLite giúp quản lý Metadata chuyên nghiệp hơn thông qua hệ quản trị cơ sở dữ liệu quan hệ (RDBMS).


        ```python
        import mlflow

        # Sử dụng SQLite để lưu trữ Metadata (thay vì file YAML)
        # Cần cài đặt: pip install sqlalchemy sqlite
        mlflow.set_tracking_uri("sqlite:///mlflow.db")

        experiment_name = "Elasticnet_SQLite"
        # Lưu ý: Khi dùng DB làm Backend Store, bạn nên chỉ định artifact_location rõ ràng
        artifact_path = "file:///D:/UDEMY/mlops_bc/mlflow_in_action/artifacts"

        if mlflow.get_experiment_by_name(experiment_name) is None:
            mlflow.create_experiment(experiment_name, artifact_location=artifact_path)
        mlflow.set_experiment(experiment_name)

        with mlflow.start_run():
            mlflow.log_param("l1_ratio", 0.1)
        ```
        </details>

    - <details>

        <summary><b>Pattern 3: Host local MLFlow Tracking Server</b></summary>

        <br>      

        Mô hình này tách biệt hoàn toàn giữa code huấn luyện (Client) và nơi lưu trữ (Server).

        - Bước 1: Chạy Server từ Terminal

            ```bash
            # Chạy lệnh này tại terminal để khởi tạo Server
            mlflow server --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./artifacts --host 127.0.0.1 --port 5000
            ```

        - Bước 2: Code kết nối từ Script/Notebook

            ```python
            import mlflow

            # Kết nối đến Server đang chạy tại localhost:5000
            mlflow.set_tracking_uri("[http://127.0.0.1:5000](http://127.0.0.1:5000)")

            # Lúc này mọi thao tác log sẽ được gửi qua HTTP request tới Server
            mlflow.set_experiment("Elasticnet_Remote_Local")
            with mlflow.start_run():
                mlflow.log_param("env", "local_server")
            ```
        </details>