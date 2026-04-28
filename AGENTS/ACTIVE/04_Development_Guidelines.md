# Development Guidelines & Troubleshooting

## Status
[Active]

## Context
CareVL do nguoi va AI cung lam. Khong co luat cung thi de vo moi truong, lech dependency, va phat sinh loi kho lan.

## Decision
Lam theo cac luat sau:

1. Shell: dung `workdir`, khong `cd`; tren PowerShell khong dung `&&`, dung `; if ($?)`.
2. Python: uu tien `uv run python`, khong goi `python` tran.
3. Dependency: them bang `uv add <package>` hoac sua `pyproject.toml`, roi `uv sync`.
4. Secret: `GITHUB_TOKEN`, `ENCRYPTION_KEY` va bien nhay cam nam trong `.env`; khong commit `.env`.
5. Encoding: moi file text dung UTF-8.

## Rationale
Luat nay giu moi truong lap lai duoc, de debug, va giam loi do thao tac tay. `uv` giu Python env sach. Secret tach rieng tranh ro ri. UTF-8 tranh loi font va Unicode.

## Troubleshooting
- `database is locked`: kiem tra WAL trong `app/core/database.py`.
- `Directory 'app/static' does not exist`: dam bao `app/static/.gitkeep` con ton tai.
- Loi import module: kiem tra `PYTHONPATH` hoac chay `uv run uvicorn app.main:app`.

## Related Documents
- [02. SQLite Security & Snapshots](02_SQLite_Security.md)
- [14. Bootstrap Infrastructure: One-Liner Setup](14_Bootstrap_Infrastructure.md)
- [16. Testing Guidelines](16_Testing_Guidelines.md)
