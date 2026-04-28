# Sec07: MLFlow Tracking Server

## Tóm tắt
* **Kiến trúc tách biệt:** MLflow chia dữ liệu thành **Backend Store** (Metadata nhẹ: params/metrics) và **Artifact Store** (Files nặng: model weights/images).
* **Lưu trữ linh hoạt:** Hỗ trợ từ quản lý file local đơn giản (`.yaml`) đến các hệ quản trị CSDL chuyên nghiệp (SQLite, PostgreSQL) và Cloud Storage (S3, Azure).
* **Giao tiếp chuẩn hóa:** Sử dụng **REST API** làm giao thức chính giữa Client và Server; hỗ trợ **Artifact Proxy** để bảo mật thông tin truy cập Cloud.
* **Các pattern triển khai** 
    | Nhóm | Mô hình | Backend Store (Metadata) | Artifact Store (Files) | Ưu điểm chính | Phù hợp cho |
    | :--- | :--- | :--- | :--- | :--- | :--- |
    | **Local** | **FileStore** | Local Files (`.yaml`) | Local Folder | Zero-config, chạy ngay lập tức. | Người mới bắt đầu, học cấu trúc MLflow. |
    | **Local** | **SQLite** | `mlflow.db` (SQLite) | Local Folder | Truy vấn nhanh, UI load mượt hơn FileStore. | Cá nhân làm project thực tế trên máy. |
    | **Local** | **Tracking Server** | `mlflow.db` | Local Folder | Tách biệt logic Code và Server. | Test luồng HTTP trước khi lên Cloud. |
    | **Remote** | **Standard** | Remote DB (Postgres/MySQL) | S3 / GCS / Azure | Tốc độ upload nhanh (đẩy trực tiếp lên mây). | Nhóm nhỏ, tin tưởng về quyền truy cập. |
    | **Remote** | **Proxied Access** | Remote DB | S3 / GCS (Ẩn sau Server) | **Bảo mật tuyệt đối**, không lộ Key Cloud cho Client. | Môi trường Production doanh nghiệp lớn. |
    | **Remote** | **Artifact Proxy** | Không lưu trữ | S3 / GCS / Azure | Chuyên dụng để lưu trữ và quản lý file/model. | Khi đã có hệ thống quản lý Metadata riêng. |

* **Quy trình chuẩn:** Cần thực hiện đủ hai bước **Khởi tạo** (Create) và **Kích hoạt** (Set) Experiment để điều hướng dữ liệu chính xác.
* **Quản lý tập trung:** Việc sử dụng Server giúp tách biệt môi trường huấn luyện và nơi lưu trữ, hỗ trợ làm việc nhóm và bảo mật Credentials, cho phép hệ thống dễ dàng nâng cấp từ máy cá nhân lên hạ tầng doanh nghiệp mà không cần thay đổi logic code cốt lõi.


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

### 2.2. Remote 

Khi triển khai thực tế trong doanh nghiệp, MLflow thường được cấu hình dưới dạng **Remote** để hỗ trợ làm việc nhóm và bảo mật dữ liệu. 

- So sánh 3 pattern phổ biến:
    | Tiêu chí | Standard Remote | Proxied Access | Artifact Proxy Only |
    | :--- | :--- | :--- | :--- |
    | **Cấu trúc** | Backend DB & Artifacts riêng. | Backend & Artifacts "giấu" sau Server. | Chỉ đóng vai trò cổng trung chuyển file. |
    | **Quyền truy cập** | **Client cần Credentials** của Cloud (S3/GCS). | **Client không cần Credentials** của Cloud. | Client chỉ cần kết nối tới Proxy Host. |
    | **Luồng Artifacts** | Client $\rightarrow$ Cloud Storage (Trực tiếp). | Client $\rightarrow$ MLflow Server $\rightarrow$ Cloud. | Client $\rightarrow$ Proxy Host $\rightarrow$ Storage. |
    | **Metadata** | Lưu đầy đủ vào DB. | Lưu đầy đủ vào DB. | **Không lưu trữ** Metadata. |
    | **Trường hợp dùng** | Nhóm nhỏ, ưu tiên tốc độ upload. | Doanh nghiệp ưu tiên bảo mật tuyệt đối. | Chỉ cần dùng MLflow làm kho chứa model. |


- **Code setup mẫu**:

    - <details>
        <summary><b>Pattern 1 - Standard Remote (Client trực tiếp đẩy Artifacts)</b></summary>

        <br>

        Mô hình này yêu cầu máy Client phải cấu hình quyền truy cập Cloud Storage.

        - **Bước 1: Khởi chạy Server (Phía Server - Có giữ Key)**

            ```bash
            mlflow server \
                --backend-store-uri sqlite:///mlflow.db \
                --default-artifact-root s3://my-mlflow-bucket/ \
                --host 0.0.0.0 \
                --port 5000
            ```

        - **Bước 2: Code tại máy Client**

            ```python
            import mlflow
            import os

            # 1. Cấu hình xác thực IAM User (Dùng cho máy Client)
            os.environ["AWS_ACCESS_KEY_ID"] = "your_access_key"
            os.environ["AWS_SECRET_ACCESS_KEY"] = "your_secret_key"
            os.environ["AWS_DEFAULT_REGION"] = "ap-southeast-1" # Rất quan trọng để tránh lỗi kết nối

            # 2. Kết nối tới Remote Tracking Server
            remote_server_url = "http://your-remote-server:5000"
            mlflow.set_tracking_uri(remote_server_url)

            experiment_name = "Remote_Direct_Cloud"

            # 3. Đảm bảo Experiment tồn tại trên Server trước khi log
            if mlflow.get_experiment_by_name(experiment_name) is None:
                # Lưu ý: Với Remote, artifact_location thường do Server định nghĩa sẵn khi khởi chạy
                mlflow.create_experiment(experiment_name)

            mlflow.set_experiment(experiment_name)

            with mlflow.start_run():
                mlflow.log_param("access_type", "direct_to_s3")
                
                # MLflow sẽ dùng cặp key trong os.environ để đẩy file này thẳng lên S3
                mlflow.log_artifact("model.pkl")
            ```
        </details>


    - <details>
        <summary><b>Pattern 2 - Standard Remote with Proxied Access</b></summary>

        <br>

        Trong mô hình này, **Client KHÔNG cần cài AWS CLI hay giữ Access Key**. Mọi quyền hạn (IAM Role/User) đều được cấu hình tại phía Server.

        - **Bước 1: Khởi chạy Server (Phía Server - Có giữ Key)**

            ```bash
            # Server giữ Key và chạy với flag --serve-artifacts
            export AWS_ACCESS_KEY_ID=your_key
            export AWS_SECRET_ACCESS_KEY=your_secret

            mlflow server \
                --backend-store-uri sqlite:///mlflow.db \
                --default-artifact-root s3://my-mlflow-bucket/ \
                --serve-artifacts \
                --host 0.0.0.0        
            ```


        - **Bước 2: Code tại máy Client**

            ```python
            import mlflow

            # Client chỉ cần biết URL của Server, không cần os.environ cho AWS
            mlflow.set_tracking_uri("http://your-mlflow-server:5000")

            mlflow.set_experiment("Proxied_Access_Experiment")

            with mlflow.start_run():
                mlflow.log_param("security_level", "high")
                # File model.pkl sẽ được gửi tới Server qua HTTP, 
                # rồi Server mới là đứa đẩy nó lên S3 giúp bạn.
                mlflow.log_artifact("model.pkl")
            ```




        </details>

    - <details>
        <summary><b>Pattern 3 - Artifact Proxy Only</b></summary>

        <br>

        - **Bước 1: Khởi chạy Server ở chế độ Artifacts-Only**

            ```bash
            mlflow server \
                --artifacts-only \
                --artifacts-destination s3://my-mlflow-bucket/ \
                --host 0.0.0.0
            ```

        - **Bước 2: Code tương tác với Artifacts**

            ```python
            import mlflow
            from mlflow.artifacts import log_artifact, download_artifacts

            # Thiết lập URI trỏ thẳng tới proxy host
            proxy_uri = "http://your-artifact-proxy:5000"

            # Log file mà không cần thông qua một Run cụ thể của Experiment
            # (Thường dùng cho việc quản lý các bộ Dataset lớn hoặc Model Registry riêng)
            mlflow.artifacts.log_artifact("data.zip", artifact_path="datasets", run_id=None)

            # Tải file từ kho về máy local
            download_artifacts(artifact_uri=f"{proxy_uri}/datasets/data.zip", dst_path="./local_data")
            ```

        </details>