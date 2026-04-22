- Một số đặc điểm về file YAML:
    - Ưu điểm:
        - Gọn, ít ký tự rườm rà hơn JSON.
        - Dễ viết, dễ sửa.
        - Phù hợp cho file cấu hình dài, nhiều tầng.

    - Nhược điểm:
        - Rất dễ lỗi nếu **sai thụt lề** (indent).
        - Vì tự đoán kiểu dữ liệu nên dễ sinh lỗi khó phát hiện.
        - Mỗi tool có thể đọc hơi khác nhau nên cần hiểu rõ.
        - Dễ bị lỗi nếu team không thống nhất cách viết.

    - Công dụng:
        - Dùng để lưu cấu hình (ví dụ: cấu hình server, pipeline, model, CI/CD)
        - Dễ đọc, gần giống cách con người viết.
        - Có thể ghi chú bằng `#` nên tiện giải thích trong file.

- Quy tắc parse kiểu dữ liệu của package PyYAML:

    | Parsed Type (Python) | Ghi chú | YAML Value| Output (Python)|
    |----------------------|---------|-----------|----------------|
    | Bool                | yes/no, on/off đều thành bool (chú ý!)      | true, yes, on \| false, no, off | True \| False|
    | NoneType            | Null → None                                     | null, ~, (empty)   | None |
    | Int                 | Hỗ trợ binary, octal, hex                       | 123                | 123  |
    | Float               | Số thực                                         | 1.23, 1e3          | 1.23, 1000.0 |
    | Datetime.date       | Auto parse date                                 | 2022-01-10         | datetime.date(2022, 1, 10)|
    | Datetime.datetime   | Datetime                                        | 2022-01-10T12:00:00 | datetime.datetime(2022,1,10,12,0,0)|
    | Str                 | Default nếu không match pattern                 | "abc", 'abc', abc   | "abc"  |
    | List                | Block/flow style list, key không cần **`""`** - giống như **`kwargs`** | - a, - b hoặc [a, b]| ["a", "b"]|
    | Dict                | Block/flow style dict                           | key: value hoặc {key: value}| {"key": "value"}|

- Một số case nguy hiểm:
    | YAML Input                 | Parsed Result                | Vấn đề |
    |----------------------------|------------------------------|--------|
    | yes: no                    | {True: False}                | Key bị cast thành bool |
    | date: 2022-01-10           | datetime.date                | Không phải string |
    | id: 0123                   | int (có thể octal)           | Leading zero |
    | [1, "2", true]             | list[mixed]                  | Dễ crash downstream |

