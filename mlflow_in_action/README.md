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

| Trường hợp | Cú pháp ví dụ | Kết quả lưu trữ |
| :--- | :--- | :--- |
| **Để trống (Mặc định)** | `mlflow.set_tracking_uri("")` hoặc không gọi hàm | Tự động tạo thư mục `./mlruns` ngay tại thư mục hiện hành đang chạy script. |
| **Đường dẫn tương đối** | `mlflow.set_tracking_uri("./my_experiments")` | Python + OS sẽ tự động giải mã **`os.path.abspath("./my_experiments")`**. |
| **Đường dẫn tuyệt đối** | `mlflow.set_tracking_uri("C:/mlflow_logs")` | Lưu dữ liệu vào chính xác địa chỉ được chỉ định trên ổ cứng. |
| **Chuẩn File URI** | `mlflow.set_tracking_uri("file:///D:/mlflow_data")` | Cách viết chuẩn giao thức file (sử dụng 3 dấu gạch chéo `/`). An toàn nhất để tránh lỗi ký tự đặc biệt trên Windows. |
| **Biến môi trường** | `$env:MLFLOW_TRACKING_URI="..."` | Thiết lập thông qua Terminal (PowerShell/CMD) mà không cần sửa code Python. |

## Tạo experiment mới:


| Lệnh | Ý nghĩa | Các tham số có thể truyền vào | Ví dụ cụ thể |
| :--- | :--- | :--- | :--- |
| **`mlflow.create_experiment()`** | Tạo Experiment mới và trả về ID. Thường dùng khi muốn kiểm soát vị trí lưu trữ artifact. | `name`, `artifact_location`, `tags` | `mlflow.create_experiment("Wine-Model", artifact_location="./custom_path")` |
| **`mlflow.set_experiment()`** | Thiết lập Experiment hiện hành. Nếu chưa có sẽ tự động tạo mới (Cách dùng phổ biến nhất). | `experiment_name`, `experiment_id` | `mlflow.set_experiment("Wine-Quality-Research")` |
| **`mlflow experiments create`** (CLI) | Tạo Experiment trực tiếp từ Terminal mà không cần vào code Python. | `--experiment-name` (`-n`), `--artifact-location` (`-l`) | `mlflow experiments create -n MyExperiment -l ./logs` |


