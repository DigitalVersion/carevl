# Hướng dẫn Coding & Những lỗi cần tránh

## Những lỗi cần tránh

### 1. Không dùng `cd` trong lệnh shell

```powershell
# Sai
cd somedir && command

# Đúng
command args
```

Hãy dùng `workdir` của tool thay vì đổi thư mục trong lệnh.

### 2. Không dùng `&&` trong PowerShell

```powershell
# Sai
cmd1 && cmd2

# Đúng
cmd1; if ($?) { cmd2 }
```

### 3. Không hardcode import làm vỡ lazy import (Dành cho legacy code)

- Các module OMR có thể cần `reportlab`, `qrcode`, nên phải giữ cơ chế lazy import.
- Khi thêm dependency, chạy `uv sync`.
- Luôn test import bằng `uv run python -c "from modules import X"`.

### 4. Không giả định `python` có trong `PATH`

- Dùng `uv run python`
- Hoặc `.venv\Scripts\python.exe`

### 5. Cẩn thận với encoding và ký tự

- Tất cả file text phải dùng UTF-8
- Văn bản tiếng Việt phải dùng dấu chuẩn
- Không dùng smart quotes
- Không chèn `{}` nếu không có chủ đích trong code

## Quy ước code

- Dùng UTF-8 cho toàn bộ file text
- Ưu tiên tiếng Việt có dấu trong tài liệu và UI
- Không thêm comment thừa nếu code đã rõ
