# 📖 Mục lục

* [**⚙️ Cấu hình hệ thống (Git Configurations)**](#️-git-configurations)
    * [Thiết lập danh tính (User & Email)](#thiết-lập-danh-tính)
    * [Quản lý Alias (Gõ tắt chuyên nghiệp)](#quản-lý-alias)
* [**🌿 Quản lý Nhánh (Branching)**](#-thao-tác-với-branch-và-alias)
    * [Làm việc với Nhánh Local (Trên máy)](#làm-việc-với-nhánh-local-trên-máy)
    * [Làm việc với Nhánh Remote (GitHub/Server)](#làm-việc-với-nhánh-remote-githubserver)
    * [Kiểm tra Trạng thái & Kết nối](#kiểm-tra-trạng-thái--kết-nối)
* [**🔀 Gộp nhánh (Merge)**](#-gộp-nhánh-merge)
    * [Các lệnh gộp nhánh phổ biến](#các-lệnh-phổ-biến)
    * [Quy trình gộp nhánh an toàn](#quy-trình-gộp-nhánh-an-toàn-standard-workflow)
* [**⬆️ Upload code local có sẵn vào repo Github (mới)**](#đưa-code-local-vào-repo-github)

<br><br>

# Git 
## Cơ chế hoạt động
- Git quản lí code theo dòng, theo dõi sự thay đổi của từng dòng văn bản thô, không quan tâm đó là code hay dòng trống.
- Cơ chế **merge** giữa các branch:
    - Các **dòng thay đổi** sẽ được **đóng gói kèm context** (3 dòng trên và dưới) tạo thành một **Hunk**. 
    - Các **Hunk trong cùng branch đè nhau** thì sẽ được **gom lại thành 1 Hunk tổng**.
    - Khi **merge**, 2 branch sẽ **tìm node graph chung cuối cùng** rồi **mỗi Hunk** sẽ đi **so khớp context** của nó để **thay đổi code bên trong** nếu trùng context.
    - **Conflict** xảy ra khi hai Hunk đè lên nhau hoặc một người sửa dòng mà người kia dùng làm ngữ cảnh (như đổi tên hàm).

        Ví dụ:

        - Conflict do trùng vị trí:
            ```
            - Gốc (Base): x = 0
            - Nhánh A:    x = 10  (Sửa dòng 10)
            - Nhánh B:    x = 20  (Cũng sửa dòng 10)
            => Conflict: Git không biết chọn 10 hay 20.
            ```
        - Conflict do mất ngữ cảnh:
            ```
            - Gốc (Base): def ham_cu(): \n    x = 1
            - Nhánh A:    def ham_moi(): \n    x = 1 (Đổi tên hàm - làm mất context của dòng x=1)
            - Nhánh B:    def ham_cu(): \n    x = 99 (Sửa logic dòng x=1 dựa trên context là ham_cu)
            => Conflict: Nhánh B tìm 'ham_cu' để dán x=99 vào nhưng không thấy vì Nhánh A đã đổi tên.
            ```

- Xử lý **conflict**: Trưởng nhóm phải tự tay nhặt code từ hai phe HEAD và Incoming, sau đó xóa các ký hiệu đánh dấu để cứu code.

## Các lệnh thông dụng

### ⚙️ Git Configurations

Sử dụng `git config` để thiết lập danh tính và quy tắc hoạt động cho Git.

| Lệnh | Tác dụng | Phạm vi |
| :--- | :--- | :--- |
| `git config --global user.name "Your Name"` | Thiết lập tên hiển thị trên Commit | Global |
| `git config --global user.email "name@email.com"` | Thiết lập Email định danh | Global |
| `git config --local user.email "mssv@st.uit.edu.vn"` | Dùng Email sinh viên cho riêng project này | Local |
| `git config --list --show-origin` | Xem tất cả config và nguồn gốc (file nào) | All |
| `git config --list --show-scope` | Xem config kèm phân cấp ưu tiên (Local > Global) | All |
| `git config user.email` | Kiểm tra nhanh Email đang áp dụng cho project | Current |
| `git config --global init.defaultBranch main` | Đổi tên nhánh mặc định thành `main` | Global |
| `git config --global core.editor "code --wait"` | Dùng VS Code để soạn thảo/fix conflict | Global |
| `git config --global credential.helper manager` | Lưu mật khẩu vào Windows Credential Manager | Global |


- Lưu ý:
    - **`--global`**: Lưu vào file tại **`C:/Users/Admin/.gitconfig`**.
    - **`--local`**: Lưu vào file tại **`.git/config trong project`**.
    - Thứ tự ưu tiên: **Local > Global > System**.    


### 🌿 Thao tác với Branch và Alias

Chia dự án thành nhiều nhánh giúp bạn quản lý code song song và tránh gây lỗi cho bản chính.

- Làm việc với **Nhánh Local** (Trên máy)

    | Thao tác | Lệnh thực hiện |
    | :--- | :--- |
    | **Tạo nhánh mới** | `git branch <tên_nhánh>` |
    | **Chuyển sang nhánh khác** | `git checkout <tên_nhánh>` hoặc `git switch <tên_nhánh>` |
    | **Tạo và chuyển sang luôn** | `git checkout -b <tên_nhánh>` |
    | **Xem danh sách nhánh** | `git branch` |
    | **Đổi tên nhánh hiện tại** | `git branch -m <tên_mới>` |
    | **Xóa nhánh (đã merge)** | `git branch -d <tên_nhánh>` |
    | **Ép xóa nhánh (chưa merge)** | `git branch -D <tên_nhánh>` |


    **Khi chuyển nhánh**, Git sẽ xóa/thay đổi file trong thư mục hiện tại để **khớp với snapshot cuối của nhánh kia**. Nếu có code dở dang, bạn phải **`commit` hoặc `git stash`** để lưu lại, nếu không Git sẽ chặn việc chuyển nhánh để bảo vệ dữ liệu.
    | Thao tác | Lệnh thực hiện |
    | :--- | :--- |
    | **Cất code dở để chuyển nhánh** | `git stash` |
    | **Lấy lại code đã cất** | `git stash pop` |

    <br>

- Làm việc với **Nhánh Remote** (GitHub/Server)

    - **`origin`** là một **alias đại diện URL của repo Github** (hoặc các kho chứa khác như Gitlab,...).

        Thay vì mỗi lần đẩy code phải gõ link dài **`git push https://github.com/23520519/Coffee-Shop.git main`** thì chỉ cần **`git push origin main`**.

    - Có thể **add thêm alias**, ví dụ: **`git remote add uit_lab https://github.com/uit-ds200/nhom-cua-hoang.git`**.

        | Thao tác | Lệnh thực hiện |
        | :--- | :--- |
        | **Đẩy nhánh lên server (Lần đầu)** | `git push -u origin <tên_nhánh>` |
        | **Đẩy code lên nhánh hiện tại** | `git push` |
        | **Đẩy chéo nhánh (Local A -> Remote B)** | `git push origin <nhánh_A>:<nhánh_B>` |
        | **Tạo nhánh local từ remote** | `git checkout --track origin/<tên_nhánh>` |
        | **Xóa nhánh trên Remote** | `git push origin --delete <tên_nhánh>` |
        | **Cập nhật danh sách nhánh mới** | `git fetch --prune` (Xóa các nhánh "ma" trên máy) |

    - **Lưu ý:** > Khi gõ `git push origin a`, Git sẽ tự hiểu là `git push origin a:a` (đẩy từ a local lên a remote).

    <br>


- **Kiểm tra Trạng thái & Kết nối**
    | Thao tác | Lệnh thực hiện |
    | :--- | :--- |
    | **Xem nhánh đang nối với ai** | `git branch -vv` |
    | **Xem chi tiết quan hệ Remote** | `git remote show origin` |
    | **Xem nhánh & sơ đồ lịch sử** | `git log --oneline --graph --all` |
    | **Xem nhanh nhánh & tình trạng** | `git status -sb` |

    <br>


### 🔀 Gộp nhánh (Merge)

- Sử dụng khi bạn đã hoàn thành tính năng ở nhánh phụ và muốn đưa nó vào nhánh chính (`main`).

    | Thao tác | Lệnh thực hiện |
    | :--- | :--- |
    | **Gộp nhánh B vào nhánh A** | (Đứng ở A) `git merge <tên_nhánh_B>` |
    | **Hủy lệnh merge (khi bị lỗi)** | `git merge --abort` |
    | **Xem các nhánh đã gộp xong** | `git branch --merged` |
    | **Xem các nhánh chưa được gộp** | `git branch --no-merged` |

- Quy trình gộp nhánh an toàn (Standard Workflow)
    1. **Chuyển về nhánh đích:** `git checkout main`.
    2. **Cập nhật code mới nhất từ server:** `git pull origin main`.
    3. **Gộp nhánh tính năng:** `git merge feature-ocr`.
    4. **Xử lý xung đột (nếu có):** Mở file bị báo đỏ, chọn code đúng, sau đó `add` và `commit`.
    5. **Đẩy code lên server:** `git push origin main`.


<br><br>

# ⬆️ Đưa code local vào repo Github 

```bash
git init
git add .
git commit -m "Initial commit: Khởi tạo dự án"
git branch -M main
git remote add origin https://github.com/user/repo-name.git
git push -u origin main
```


- Giải thích các lệnh 💡:
    - `git init`: Tạo thư mục ẩn `.git` để bắt đầu theo dõi dự án.
    - `git branch -M main`: Đổi tên nhánh mặc định thành `main` (một số máy cũ để mặc định là `master`).
    - `git remote add origin`: Đặt biệt danh "origin" cho địa chỉ Server.
    - `git push -u`: Chữ `-u` (upstream) giúp lưu lại kết nối, lần sau bạn chỉ cần gõ `git push` là xong.
