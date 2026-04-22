# How to run

- Chạy các lệnh sau:

    ```python
    pip install flask
    python app.py
    ```

    Sau đó qua terminal mới chạy lệnh:

    ```python
    pytest test_app.py
    ```

- Kết quả: Trả về lỗi vì app chạy ở port 5001 chứ không phải 5005

    ```pytest
    ........................Còn nữa ở trên.....
            except requests.exceptions.RequestException as e :
    >           pytest.fail(f"Application at {url} is not available. Error : {e}")
    E           Failed: Application at http://127.0.0.1:5005/ is not available. Error : HTTPConnectionPool(host='127.0.0.1', port=5005): Max retries exceeded with url: / (Caused by NewConnectionError("HTTPConnection(host='127.0.0.1', port=5005): Failed to establish a new connection: [WinError 10061] No connection could be made because the target machine actively refused it"))

    test_app.py:10: Failed
    ================================================================ SHORT TEST SUMMARY INFO ============================
    FAILED test_app.py::test_app_running - Failed: Application at http://127.0.0.1:5005/ is not available. Error : HTTPConnectionPool(host='127.0.0.1', port=5005): Max retries exceeded with ur...
    =================================================================== 1 failed in 2.45s ===============================
    ```