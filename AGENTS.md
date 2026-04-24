# AGENTS.md — Hướng Dẫn Phát Triển CareVL

> **Quan trọng: Đọc file này trước khi sửa bất kỳ phần nào trong repo.**

---

## Tổng quan dự án

**CareVL** (Care Vinh Long) là ứng dụng desktop quản lý hồ sơ khám sức khỏe cho tỉnh Vĩnh Long.

- **Stack**: Python 3.11+, CustomTkinter, SQLite local, Git sync, DuckDB cho Hub
- **Nền tảng**: Windows, offline-first
- **Xác thực**: GitHub OAuth Device Flow

---

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

### 3. Không hardcode import làm vỡ lazy import

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

---

## Cấu trúc chính

```text
carevl/
├── main.py
├── launcher.bat
├── pyproject.toml
├── .gitignore
├── config/
├── data/
│   └── carevl.db
├── modules/
├── ui/
└── dist/
```

### `config/`

- `template_form.json`: cấu hình form động
- `user_config.json`: token OAuth, không được commit
- `omr_form_layout.json`: layout OMR
- `omr_templates/`: template OMR theo gói khám

### `data/`

- `carevl.db`: SQLite local dùng cho runtime

### `modules/`

- `__init__.py`: lazy import, không được làm hỏng
- `auth.py`: đăng nhập GitHub
- `crud.py`: facade runtime
- `crud_phase2.py`: CRUD SQLite phase 2
- `record_store.py`: storage facade
- `sync.py`: Git push/pull
- `validator.py`: validate dữ liệu
- `form_engine.py`: render form động
- `omr_*`: pipeline OMR

### `ui/`

- `app.py`: app chính
- `screen_list.py`: danh sách hồ sơ
- `screen_form.py`: nhập và sửa hồ sơ
- `screen_sync.py`: đồng bộ

---

## File quan trọng

### `modules/__init__.py`

File này dùng `importlib` để lazy-load module. Không được đổi sang kiểu import trực tiếp làm vỡ hành vi runtime.

### `config/user_config.json`

Chứa token OAuth. Phải nằm trong `.gitignore`. Không commit.

---

## Khi thêm dependency

1. Cập nhật `pyproject.toml`
2. Chạy `uv sync`
3. Test import bằng `uv run python -c "import ten_goi; print('OK')"`

---

## Cách test cơ bản

```powershell
# Chạy app
uv run python main.py

# Kiểm tra backend lưu trữ hiện tại
uv run python -c "from modules import record_store; print(record_store.get_storage_path())"

# Kiểm tra import module
uv run python -c "from modules import crud; print('OK')"

# Kiểm tra lệnh OMR
uv run python -m modules.omr_form_gen --help
```

---

## Build executable

```powershell
uv run pyinstaller --onefile --windowed --name carevl main.py
```

Output ở `dist/carevl.exe`.

---

## Quy ước code

- Giữ lazy import
- Dùng UTF-8 cho toàn bộ file text
- Ưu tiên tiếng Việt có dấu trong tài liệu và UI
- Không thêm comment thừa nếu code đã rõ

---

## Pipeline OMR

Các module OMR chạy độc lập, chưa tích hợp thành menu chính trong app:

```powershell
# Tạo PDF từ CCCD
python -m modules.omr_form_gen --cccd 001286001234 --package nct --output form.pdf

# Đọc batch scan
python -m modules.omr_reader --input scans/ --output results/ --package nct --json results.json

# Map và lưu
python -m modules.omr_bridge --input results.json --package nct --save --author bacsi01
```

---

## Lệnh hay dùng

| Tác vụ | Lệnh |
|---|---|
| Chạy app | `uv run python main.py` |
| Đồng bộ dependency | `uv sync` |
| Test import | `uv run python -c "from modules import X"` |
| Build exe | `uv run pyinstaller --onefile --windowed --name carevl main.py` |
| OMR gen | `uv run python -m modules.omr_form_gen --help` |
| OMR read | `uv run python -m modules.omr_reader --help` |

---

## Xử lý sự cố

### Thiếu `reportlab`

- Chạy `uv sync`
- Nếu cần, xóa `.venv` rồi sync lại

### Lỗi import

- Dùng `uv run python`, không dùng `python` trần
- Kiểm tra lại lazy import trong `modules/__init__.py`

### Lỗi encoding JSON

- Dùng `encoding="utf-8"`
- Dùng `ensure_ascii=False` khi ghi JSON

---

*Cập nhật gần nhất: 2026-04-24*
