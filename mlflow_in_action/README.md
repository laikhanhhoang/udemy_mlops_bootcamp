# Sec03: Tracking Component
## Các bảng chính của MLFlow DB trong Tracking Component

- 📑 **Experiments & Runs**: Quản lý **định danh thí nghiệm và các lần chạy**.

    | Bảng | Cột khóa | Các cột khác | Ý nghĩa |
    | :--- | :--- | :--- | :--- |
    | **Experiments** | `experiment_id` (PK) | `name`, `artifact_location`, `lifecycle_stage` | Quản lý định danh và nơi lưu trữ của một nhóm thực nghiệm. |
    | **Runs** | `run_id` (PK) | `experiment_id` (FK), `status`, `start_time`, `end_time`, `lifecycle_stage` | Chi tiết về một phiên chạy huấn luyện cụ thể. |


- 📈 **Tracking Data** (Nội dung thực nghiệm): **Lưu trữ các thông số kỹ thuật và kết quả đo lường**.

    | Bảng | Cột khóa | Các cột khác | Ý nghĩa |
    | :--- | :--- | :--- | :--- |
    | **Metrics** | `run_id` (FK) | `key`, `value`, `timestamp`, `step` | Lưu trữ các kết quả đo lường (RMSE, R2) theo thời gian. |
    | **Params** | `run_id` (FK) | `key`, `value` | Lưu trữ các tham số cấu hình (Alpha, L1_Ratio) của mô hình. |
    | **Tags** | `run_id` (FK) | `key`, `value` | Các nhãn thông tin bổ sung (tên model, loại dataset). |
    | **Artifacts** | `run_id` (FK) | `artifact_path`, `file_type`, `location` | Quản lý các file vật lý (file .pkl, ảnh đồ thị) được lưu trữ. |

<div align="center">
    <img src="imgs/mlrun_a_db_demo.png" width=1000>
    <br>
    <i>Demo folder mlruns/ và mlflow.db</i>
</div>

## Các loại URI Scheme trong Tracking Component


| Scheme | Cách dùng | Ý nghĩa |
| :--- | :--- | :--- |
| **`runs:/`** | `runs:/<run_id>/<path>` | Truy cập tài nguyên (artifacts/data) thuộc về một Run cụ thể thông qua ID. |
|**`models:/`** | `models:/<name>/<version_or_stage>` | Truy cập tài nguyên đã được đăng ký trong Model Registry. |
|**`file:/`** | `file:/path/to/directory` | Truy cập tài nguyên trực tiếp từ hệ thống tệp cục bộ (Local Filesystem). |


<br><br><br>

# Sec04: Logging Functions Local

## Setup folder tracking **`mlflow.set_tracking_uri()`**:

- Tracking URI là **endpoint mà MLflow client dùng để tracking data**(runs, experiments, artifacts).

    Có thể là **filesystem path (file:///...)** hoặc **HTTP endpoint (http://...)**,...

| Trường hợp | Cú pháp ví dụ | Kết quả lưu trữ |
| :--- | :--- | :--- |
| **Để trống (Mặc định)** | `mlflow.set_tracking_uri("")` hoặc không gọi hàm | Tự động tạo thư mục `./mlruns` ngay tại thư mục hiện hành đang chạy script. |
| **Đường dẫn tương đối** | `mlflow.set_tracking_uri("./my_experiments")` | Python + OS sẽ tự động giải mã **`os.path.abspath("./my_experiments")`**. |
| **Đường dẫn tuyệt đối** | `mlflow.set_tracking_uri("C:/mlflow_logs")` | Lưu dữ liệu vào chính xác địa chỉ được chỉ định trên ổ cứng. |
| **Chuẩn File URI** | `mlflow.set_tracking_uri("file:///D:/mlflow_data")` | **Sử dụng giao thức file local** (sử dụng 3 dấu gạch chéo `/`) **thay vì DB** như các cách trên. Thường dùng cho **tracking local**. |
| **Biến môi trường** | `$env:MLFLOW_TRACKING_URI="..."` | Thiết lập thông qua Terminal (PowerShell/CMD) mà không cần sửa code Python. |


## Tạo experiment mới:

| Lệnh | Ý nghĩa | Các tham số có thể truyền vào | Ví dụ cụ thể |
| :--- | :--- | :--- | :--- |
| **`mlflow.create_experiment()`** | Tạo Experiment mới và trả về ID. Thường dùng khi muốn kiểm soát vị trí lưu trữ artifact. | `name`, `artifact_location`, `tags` | `mlflow.create_experiment("Wine-Model", artifact_location="./custom_path")` |
| **`mlflow.set_experiment()`** | Thiết lập Experiment hiện hành. Nếu chưa có sẽ tự động tạo mới (Cách dùng phổ biến nhất). | `experiment_name`, `experiment_id` | `mlflow.set_experiment("Wine-Quality-Research")` |
| **`mlflow experiments create`** (CLI) | Tạo Experiment trực tiếp từ Terminal mà không cần vào code Python. | `--experiment-name` (`-n`), `--artifact-location` (`-l`) | `mlflow experiments create -n MyExperiment -l ./logs` |


## 🏁 Lệnh Bắt đầu/Kết thúc Run (Experiment Execution)

| Lệnh | Ý nghĩa | Các tham số có thể truyền vào | Ví dụ cụ thể |
| :--- | :--- | :--- | :--- |
| **`mlflow.start_run()`** | Khởi tạo một phiên chạy (Run) mới để bắt đầu ghi log dữ liệu. | `run_id`, `experiment_id`, `run_name`, `nested` (True/False) | `with mlflow.start_run(run_name="ElasticNet_Baseline"):` |
| **`mlflow.end_run()`** | Kết thúc phiên chạy hiện tại. Thường dùng khi không sử dụng cấu trúc `with`. | `status` (FINISHED, FAILED, KILLED) | `mlflow.end_run(status="FINISHED")` |
| **`mlflow.active_run()`** | Lấy thông tin về Run đang hoạt động (nếu có). | Không có | `run = mlflow.active_run()` <br> `print(run.info.run_id)` |
| **`mlflow.last_active_run()`** | Truy xuất thông tin của Run được kích hoạt gần đây nhất. | Không có | `run = mlflow.last_active_run()` <br> `print(run.info.run_id)` |

- Lưu ý về cách sử dụng:
    * **Sử dụng `with` (Khuyên dùng):** Khi dùng `with mlflow.start_run():`, MLflow sẽ tự động gọi `end_run()` cho bạn khi khối lệnh kết thúc hoặc nếu gặp lỗi giữa chừng. Điều này giúp trạng thái của Run luôn chính xác (thường là `FINISHED` hoặc `FAILED`).
    * **Nested Runs:** Nếu bạn đang thực hiện Cross Validation, bạn có thể đặt `nested=True` để tạo ra các Run con nằm bên trong một Run cha, giúp tổ chức dữ liệu trên UI gọn gàng hơn.
    * **Run Name:** Đừng quên đặt `run_name` để thay thế cho những cái tên ngẫu nhiên mặc định, giúp bạn dễ dàng nhận diện phiên bản mô hình nào đang hoạt động tốt.


## Các lệnh Log Metadata trong MLflow

### 1. Ghi log đơn lẻ (Individual Logging)
| Lệnh | Ý nghĩa | Tham số truyền vào | Ví dụ cụ thể |
| :--- | :--- | :--- | :--- |
| **`mlflow.log_param()`** | Ghi log một tham số đầu vào (Hyperparameter). | `key`, `value` | `mlflow.log_param("learning_rate", 0.01)` |
| **`mlflow.log_metric()`** | Ghi log một chỉ số kết quả (thường là số). | `key`, `value`, `step` | `mlflow.log_metric("rmse", 0.123)` |
| **`mlflow.set_tag()`** | Ghi log thông tin bổ trợ để phân loại/lọc Run. | `key`, `value` | `mlflow.set_tag("release.candidate", "v1.0")` |
| **`mlflow.log_artifact()`** | Ghi log một file vật lý (ảnh, csv, txt...) | `local_path`, `artifact_path` | `mlflow.log_artifact("plot.png")` |

### 2. Ghi log hàng loạt (Batch/Bulk Logging)
| Lệnh | Ý nghĩa | Tham số truyền vào | Ví dụ cụ thể |
| :--- | :--- | :--- | :--- |
| **`mlflow.log_params()`** | Ghi hàng loạt tham số từ một Dictionary. | `params` (dict) | `mlflow.log_params({"alpha": 0.5, "l1": 0.1})` |
| **`mlflow.log_metrics()`** | Ghi hàng loạt chỉ số từ một Dictionary. | `metrics` (dict), `step` | `mlflow.log_metrics({"rmse": 0.1, "mae": 0.2})` |
| **`mlflow.set_tags()`** | Ghi hàng loạt tags từ một Dictionary. | `tags` (dict) | `mlflow.set_tags({"env": "dev", "user": "dat"})` |
| **`mlflow.log_artifacts()`** | Ghi log toàn bộ file trong một thư mục. | `local_dir`, `artifact_path` - đổi tên folder khi log vào **`mlruns`** | `mlflow.log_artifacts("outputs/", "plots")` |


### Lưu ý quan trọng:
* **Giá trị Metrics:** `log_metric` bắt buộc phải là số (int hoặc float) để MLflow có thể vẽ biểu đồ trực quan trên UI.
* **Tham số Step:** Sử dụng `step` trong `log_metric` khi bạn muốn theo dõi sự thay đổi của chỉ số qua từng vòng lặp (epoch).
* **Hiệu năng:** Nên ưu tiên các lệnh ghi hàng loạt (batch commands) như `log_params` để giảm số lượng yêu cầu gửi đến server, giúp code chạy nhanh hơn.

