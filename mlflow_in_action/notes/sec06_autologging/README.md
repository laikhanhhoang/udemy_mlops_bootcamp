# Sec06: Autologging
Cách thức hoạt động: MLflow sẽ "hook" vào các thư viện phổ biến (như Scikit-learn, TensorFlow, PyTorch, XGBoost...) để tự động thu thập dữ liệu ngay khi lệnh `.fit()` được gọi.
### 1. Các thành phần chính được Autolog ghi lại
Mặc định, khi gọi `mlflow.sklearn.autolog()`, MLflow sẽ thu thập:
* **Parameters:** Toàn bộ tham số khởi tạo của estimator (ví dụ: `alpha`, `copy_X`, `l1_ratio`, `max_iter`, v.v.).
* **Metrics:** Các chỉ số huấn luyện (như `training_score`, `training_rmse`...).
* **Tags:** Tên class của estimator, phiên bản thư viện.
* **Artifacts:** File mô hình (`model.pkl`), cấu hình môi trường (`conda.yaml`, `requirements.txt`).
* **Schemas:** Model signature (cấu trúc input/output).

### 2. Cách bật/tắt logging từng tham số
Bạn có thể điều chỉnh các tham số bên trong hàm `autolog()` để quyết định thành phần nào được ghi log. Dưới đây là các tham số phổ biến:

| Tham số | Ý nghĩa | Mặc định |
| :--- | :--- | :--- |
| **`log_params`** | Bật/tắt ghi log các tham số khởi tạo mô hình. | `True` |
| **`log_metrics`** | Bật/tắt ghi log các chỉ số đánh giá. | `True` |
| **`log_models`** | Bật/tắt việc lưu file mô hình (Artifacts). | `True` |
| **`log_input_examples`** | Ghi lại một vài dòng dữ liệu mẫu để làm ví dụ. | `False` |
| **`log_model_signatures`** | Ghi lại định dạng dữ liệu đầu vào và đầu ra. | `True` |

**Mẹo:** Trong thực tế, nếu bạn đang thực hiện Grid Search với hàng nghìn lần chạy, bạn nên cân nhắc đặt **`log_models=False`** để tránh việc lưu hàng nghìn file mô hình, gây lãng phí tài nguyên. Chỉ nên bật lại (**`True`**) cho phiên chạy cuối cùng với bộ tham số tối ưu nhất.

### 3. Ví dụ cấu hình cụ thể
Nếu bạn chỉ muốn log Parameters và Metrics nhưng không muốn lưu file Model (để tiết kiệm dung lượng ổ đĩa), bạn có thể cấu hình như sau:

```python
import mlflow

# Cấu hình chi tiết: Chỉ log tham số và chỉ số, tắt lưu file mô hình
mlflow.sklearn.autolog(
    log_models=False,           # Tắt lưu file mô hình
    log_params=True,            # Vẫn giữ lại tham số
    log_metrics=True,           # Vẫn giữ lại chỉ số
    log_input_examples=False    # Không lưu dữ liệu mẫu
)

with mlflow.start_run():
    # Khi gọi fit, file mô hình sẽ không được đẩy lên artifact store
    lr.fit(train_x, train_y)
```

### 4. Tắt Autologging hoàn toàn

Nếu bạn muốn dừng việc tự động ghi log cho một thư viện cụ thể hoặc tắt toàn bộ, bạn có thể sử dụng tham số disable:

```python
# Tắt tính năng tự động ghi log cho Scikit-learn
mlflow.sklearn.autolog(disable=True)

# Hoặc tắt tất cả các thư viện đang được autolog (toàn cục)
mlflow.autolog(disable=True)
```