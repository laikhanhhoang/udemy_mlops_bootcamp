# Sec05: Launch Multiple Experiments

Phần này hướng dẫn cách thực hiện nhiều phiên chạy (Multiple Runs) trong cùng một thí nghiệm để so sánh các bộ siêu tham số (Hyperparameters), sử dụng cơ chế **Nested Runs** của MLflow.

## 1. Khái niệm Nested Runs (Chạy lồng nhau)
Khi thực hiện Hyperparameter Tuning (như Grid Search), việc tạo hàng chục Run đơn lẻ sẽ làm giao diện MLflow UI bị rối. 
* **Parent Run (Run cha):** Đại diện cho toàn bộ đợt Tuning (ví dụ: Grid Search).
* **Child Run (Run con):** Mỗi bộ tham số `(alpha, l1_ratio)` cụ thể sẽ là một Run con bên trong.

## 2. Cách triển khai trong Code
Để thực hiện, chúng ta sử dụng tham số `nested=True` trong lệnh `mlflow.start_run()`.

```python
# Cấu trúc mẫu để chạy Multiple Experiments
with mlflow.start_run(run_name="Parent_Grid_Search"):
    for a in [0.1, 0.5, 0.9]:
        for l1 in [0.2, 0.8]:
            # Khởi tạo Run con
            with mlflow.start_run(run_name=f"a_{a}_l1_{l1}", nested=True):
                # Huấn luyện và log dữ liệu như bình thường
                mlflow.log_params({"alpha": a, "l1_ratio": l1})
                # ...
```


## 3. Log vào Parent Run

Trong kiến trúc Nested Runs, **Parent Run** không chỉ là một lớp vỏ bọc mà là một Run thực thụ. Việc ghi log vào Parent Run giúp lưu trữ các thông tin mang tính tổng quan hoặc kết quả cuối cùng của toàn bộ đợt thí nghiệm.

### 3.1. Cơ chế Stack (Ngăn xếp) của MLflow
MLflow quản lý các Run theo cơ chế ngăn xếp. Lệnh ghi log (`mlflow.log_...`) sẽ luôn tác động vào Run nào được mở **gần nhất** mà chưa đóng.

* **Log vào Parent:** Thực hiện lệnh log bên ngoài khối lệnh `nested=True`.
* **Log vào Child:** Thực hiện lệnh log bên trong khối lệnh `nested=True`.

### 3.2. Ví dụ triển khai

```python
with mlflow.start_run(run_name="Grid_Search_ElasticNet") as parent_run:
    # 1. Ghi thông tin tổng quan vào Parent Run
    mlflow.set_tag("dataset", "Wine-Quality-v1")
    mlflow.log_param("total_trials", len(alphas) * len(l1_ratios))

    for a in alphas:
        for l1 in l1_ratios:
            # Bắt đầu Run con
            with mlflow.start_run(run_name=f"Trial_a{a}_l1{l1}", nested=True):
                # 2. Ghi thông tin chi tiết vào Child Run
                mlflow.log_params({"alpha": a, "l1_ratio": l1})
                mlflow.log_metric("rmse", current_rmse)
                # (Khi kết thúc khối with này, Child Run sẽ đóng lại)

    # 3. Ghi kết quả tốt nhất tìm được vào Parent Run (sau khi các con đã chạy xong)
    mlflow.log_metric("best_rmse", final_best_rmse)
    mlflow.set_tag("status", "Optimization Finished")
```