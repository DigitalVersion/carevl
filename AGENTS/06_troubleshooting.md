# Xử lý sự cố (Troubleshooting)

### Lỗi `database is locked` trên SQLite

- Chắc chắn rằng WAL mode được kích hoạt thông qua connection event của SQLAlchemy.
- Không thay đổi `PRAGMA` bên trong các active transaction.

### Lỗi khi start FastAPI (`Directory 'app/static' does not exist`)

- Thư mục trống thường không được git theo dõi. Chắc chắn đã có file `.gitkeep` trong `app/static/`.

### Thiếu Dependency

- Chạy `uv sync`.
- Nếu cần, xóa `.venv` rồi sync lại.

### Lỗi import

- Dùng `uv run python`, không dùng `python` trần.

### Lỗi encoding JSON

- Dùng `encoding="utf-8"`.
- Dùng `ensure_ascii=False` khi ghi JSON.
