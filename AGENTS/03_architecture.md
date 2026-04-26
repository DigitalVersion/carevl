# Kiến trúc và Cấu trúc dự án

## Cấu trúc chính

```text
carevl/
├── app/               # FastAPI Backend & Web UI
│   ├── api/           # Router endpoints
│   ├── core/          # Config, Identity, DB setup
│   ├── models/        # SQLAlchemy Models
│   ├── schemas/       # Pydantic Schemas
│   ├── services/      # Logic, Crypto, Auto-Snapshot
│   ├── static/        # Static assets
│   └── templates/     # Jinja2 HTML templates
├── legacy/            # Archived CustomTkinter code
├── data/              # SQLite local store (.db and .db.enc)
├── pyproject.toml
├── .env.example
└── .gitignore
```

## File quan trọng

### `.env` và `app/core/config.py`

Quản lý biến môi trường của hệ thống (SITE_ID, GITHUB_TOKEN, ENCRYPTION_KEY). `.env` tuyệt đối không được commit.

### `app/core/database.py`

Cấu hình kết nối SQLAlchemy tới SQLite. Đặc biệt quan trọng: Cơ chế WAL (Write-Ahead Logging) được kích hoạt qua connection event.
