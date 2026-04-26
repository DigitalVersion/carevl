# Quy trình Phát triển

## Khi thêm dependency

1. Cập nhật qua `uv add <package>` hoặc sửa `pyproject.toml`
2. Chạy `uv sync`
3. Test import bằng `uv run python -c "import ten_goi; print('OK')"`

## Cách test cơ bản

```bash
# Chạy app FastAPI (Dev Server)
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Chạy test suite
uv run pytest app/tests.py
```

## Lệnh hay dùng

| Tác vụ | Lệnh |
|---|---|
| Chạy FastAPI | `uv run uvicorn app.main:app --reload` |
| Đồng bộ dependency | `uv sync` |
| Chạy tests | `uv run pytest app/tests.py` |
| Legacy App | `uv run python legacy/main.py` |
