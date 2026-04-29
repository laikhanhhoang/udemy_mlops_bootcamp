# Section 13: MlflowClient()

## 1. Tại sao sử dụng MlflowClient() thay vì dùng thẳng các hàm Mlflow?

Mặc dù các hàm Fluent API như `mlflow.start_run()` rất tiện lợi, nhưng `MlflowClient()` là lựa chọn tối ưu cho các kịch bản quản trị và tự động hóa:

*   **Kiểm soát chi tiết (Fine-grained Control):** **Thao tác trực tiếp** với bất kỳ Experiment, Run, hoặc Model mà **không cần thiết lập trạng thái "active"**.
*   **Quản lý từ xa & Admin:** Phù hợp để viết các script dọn dẹp dữ liệu, quản lý quyền truy cập hoặc tích hợp vào pipeline CI/CD.
*   **Tính năng độc quyền:** **Các thao tác nâng cao** trong **Model Registry** (như xóa phiên bản, đổi tên mô hình, gán tag cho version) **bắt buộc phải dùng Client**.
*   **Truy vấn đa nhiệm:** Dễ dàng so sánh dữ liệu giữa nhiều Experiment khác nhau trong cùng một script.

---

## 2. Các hàm MlflowClient() phổ biến

| Hàm | Tham số chủ yếu | Hành động thực hiện |
| :--- | :--- | :--- |
| **search_experiments** | `view_type`, `filter_string`, `order_by` | Tìm kiếm thí nghiệm theo điều kiện lọc (tags, name) và sắp xếp. |
| **create_registered_model** | `name`, `tags`, `description` | Khởi tạo một định nghĩa Model mới trong Registry. |
| **get_registered_model** | `name` | Lấy thông tin chi tiết của một Model đã đăng ký. |
| **update_registered_model** | `name`, `description` | Cập nhật mô tả tổng quát cho Model. |
| **delete_registered_model** | `name` | Xóa vĩnh viễn Model và toàn bộ các phiên bản thuộc về nó. |
| **rename_registered_model** | `name`, `new_name` | Thay đổi tên định danh của Model. |
| **search_registered_models** | `filter_string`, `max_results` | Tìm kiếm danh sách các Model dựa trên tên hoặc tag. |
| **create_model_version** | `name`, `source`, `run_id` | Đăng ký một phiên bản mới (v1, v2...) từ một Run cụ thể. |
| **get_model_version** | `name`, `version` | Lấy thông tin chi tiết (trạng thái, ngày tạo) của một version. |
| **update_model_version** | `name`, `version`, `description` | Cập nhật ghi chú cho một phiên bản cụ thể. |
| **delete_model_version** | `name`, `version` | Xóa bỏ một phiên bản nhất định khỏi Registry. |
| **set_model_version_tag** | `name`, `version`, `key`, `value` | Gắn nhãn (như `stage: production`) cho một version cụ thể. |
| **set_registered_model_tag** | `name`, `key`, `value` | Gắn nhãn cấp cao cho Model (áp dụng cho toàn bộ các version). |

---

## 3. Code mẫu triển khai
```python
from mlflow.tracking import MlflowClient
from mlflow.entities import ViewType

client = MlflowClient()

# --- 1. Quản lý Experiment ---
# Tìm kiếm các thí nghiệm có tag version='v1'
experiments = client.search_experiments(
    view_type=ViewType.ALL,
    filter_string="tags.`version` = 'v1' AND tags.`framework` = 'sklearn'",
    order_by=["experiment_id ASC"]
)

# --- 2. Quản lý Registered Model ---
model_name = "Sklearn_LR_Model"

# Tạo Model Registry
client.create_registered_model(model_name, tags={"task": "regression"})

# Cập nhật thông tin
client.update_registered_model(model_name, description="Mô hình dự báo giá nhà")
client.set_registered_model_tag(model_name, "team", "AI_Core")

# --- 3. Quản lý Model Version ---
# Giả sử lấy model từ một Run ID đã hoàn thành
run_id = "your_run_id_here"
source_uri = f"runs:/{run_id}/model"
mv = client.create_model_version(model_name, source_uri, run_id)

# Gán tag cho version để đánh dấu trạng thái Deployment
client.set_model_version_tag(model_name, mv.version, "status", "candidate")

# --- 4. Truy vấn thông tin ---
version_detail = client.get_model_version(model_name, mv.version)
print(f"Model: {version_detail.name}, Version: {version_detail.version}, Tag: {version_detail.tags}")
```
- **Lưu ý quan trọng:**
    - Đối với các hàm `set_registered_model_tag` và `set_model_version_tag`, hãy đảm bảo **tên model** và **số version** hoàn toàn chính xác để tránh lỗi `MlflowException`.
    - Các **ID** và **Tên mô hình** trong Model Registry luôn **phân biệt chữ hoa chữ thường** (Case-sensitive). 
    
        *Ví dụ:* `MyModel` và `mymodel` sẽ được hiểu là hai thực thể hoàn toàn khác nhau.