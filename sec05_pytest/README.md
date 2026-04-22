# Pytest - Quick Guide

## Pytest là gì

Pytest là thư viện dùng để viết và chạy test trong Python, giúp kiểm tra code có chạy đúng hay không.

---

## Cài đặt

```bash
pip install pytest
```

---

## Cách viết test đơn giản

```python
def add(a, b):
    return a + b

def test_add():
    assert add(1, 2) == 3
```

---

## Cách chạy test

```bash
pytest
```

---

## Quy tắc đặt tên

* File: `test_*.py` hoặc `*_test.py`
* Hàm: bắt đầu bằng `test_`

---

## Fixture (chuẩn bị dữ liệu)

```python
import pytest

@pytest.fixture
def data():
    return [1, 2, 3]

def test_sum(data):
    assert sum(data) == 6
```

---

## Test nhiều trường hợp

```python
import pytest

@pytest.mark.parametrize("a,b,expected", [
    (1, 2, 3),
    (0, 0, 0),
])
def test_add(a, b, expected):
    assert add(a, b) == expected
```

---

## Một số option hay dùng

```bash
pytest -v        # chi tiết
pytest -q        # gọn
pytest -k "add"  # lọc test
```

---

## Lưu ý

* Test phải có `assert` rõ ràng
* Tránh gọi API thật trong test
* Không phụ thuộc vào trạng thái bên ngoài

---

## Tóm lại

* Pytest giúp kiểm tra code tự động
* Dễ viết, dễ dùng
* Phù hợp từ project nhỏ đến production
