# Monorepo Migration Complete

## Status
[Active - Implemented]

## Context
Code cu nam trong `app/` khong tach biet Edge va Hub. Can tach thanh monorepo de:
- Tach biet Edge (tram) va Hub (tinh)
- Giu code dung chung trong `shared/`
- De deploy rieng biet
- Bao mat tot hon

## Decision
Da tach thanh monorepo structure theo 18_Two_App_Architecture.md.

### Cau truc moi
```
carevl/
├── edge/              # Edge app cho tram
│   ├── app/          # FastAPI application
│   │   ├── api/      # Routes
│   │   ├── core/     # Config, database
│   │   ├── models/   # SQLAlchemy models (13 models)
│   │   ├── schemas/  # Pydantic schemas
│   │   ├── services/ # Business logic
│   │   ├── static/   # CSS, JS
│   │   ├── templates/# Jinja2 templates
│   │   └── main.py   # FastAPI app
│   ├── tests/        # Tests
│   ├── pyproject.toml# Edge dependencies
│   ├── README.md     # Edge docs
│   └── __init__.py
├── hub/               # Hub CLI cho tinh
│   ├── carevl_hub/   # CLI application
│   │   ├── cli.py    # Typer CLI entry
│   │   ├── config.py # Settings
│   │   ├── downloader.py # GitHub download
│   │   ├── aggregator.py # DuckDB aggregation
│   │   └── __init__.py
│   ├── tests/        # Tests
│   ├── pyproject.toml# Hub dependencies
│   ├── README.md     # Hub docs
│   └── __init__.py
├── shared/            # Shared utilities
│   ├── crypto.py     # Encryption/decryption (AES-256)
│   ├── models.py     # Pydantic models (10 models)
│   ├── constants.py  # Constants (100+ constants)
│   ├── README.md     # Shared docs
│   └── __init__.py
├── scripts/           # Build and migration scripts
│   ├── schema_phase2.sql
│   ├── migrate_to_phase2.py
│   └── setup.ps1
├── AGENTS/            # Documentation (19 ACTIVE docs)
├── legacy/            # Old code (deprecated)
│   ├── modules/
│   ├── ui/
│   └── main.py
└── pyproject.toml     # Root workspace config
```

### Dependencies

**Edge (`edge/pyproject.toml`):**
- fastapi, uvicorn
- sqlalchemy
- cryptography
- httpx
- jinja2
- apscheduler
- pydantic

**Hub (`hub/pyproject.toml`):**
- typer (CLI)
- duckdb (analytics)
- pandas
- httpx
- cryptography
- openpyxl (Excel)
- pydantic

**Shared:**
- cryptography
- pydantic

**Root (`pyproject.toml`):**
- Workspace config
- Dev dependencies (pytest, mypy)

### Workflow dev

**Edge:**
```bash
cd edge
uv sync
uv run uvicorn app.main:app --reload
uv run pytest
```

**Hub:**
```bash
cd hub
uv sync
uv run python -m carevl_hub.cli --help
uv pip install -e .
uv run pytest
```

**Shared:**
```python
# Import in Edge
from shared.crypto import encrypt_snapshot
from shared.constants import SYNC_STATE_PENDING

# Import in Hub
from shared.crypto import decrypt_snapshot
from shared.models import SnapshotMetadata
```

### Build & Deploy

**Edge:**
```bash
cd edge
uv run pyinstaller carevl.spec
# Output: dist/carevl.exe
```

**Hub:**
```bash
cd hub
uv pip install -e .
# Or publish to PyPI
```

### Files created

**Shared (5 files):**
- `shared/__init__.py`
- `shared/crypto.py` (copied from app/services/crypto.py)
- `shared/models.py` (10 Pydantic models)
- `shared/constants.py` (100+ constants)
- `shared/README.md`

**Hub (7 files):**
- `hub/__init__.py`
- `hub/carevl_hub/__init__.py`
- `hub/carevl_hub/cli.py` (Typer CLI with 7 commands)
- `hub/carevl_hub/config.py` (Settings)
- `hub/carevl_hub/downloader.py` (GitHub API)
- `hub/carevl_hub/aggregator.py` (DuckDB)
- `hub/README.md`

**Edge (3 files):**
- `edge/__init__.py`
- `edge/pyproject.toml`
- `edge/README.md`
- `edge/app/` (copied from `app/`)

**Root (3 files):**
- `pyproject.toml` (updated to workspace)
- `MONOREPO_MIGRATION.md`
- `AGENTS/ACTIVE/20_Monorepo_Migration_Complete.md`

### Next steps

- [ ] Update imports in Edge app: `from shared.crypto import ...`
- [ ] Test Edge app: `cd edge && uv run uvicorn app.main:app --reload`
- [ ] Test Hub CLI: `cd hub && uv run python -m carevl_hub.cli --help`
- [ ] Implement Hub CLI commands (download, decrypt, aggregate, report)
- [ ] Update CI/CD to build Edge and Hub separately
- [ ] Move old code to `legacy/`
- [ ] Update bootstrap script to download from new structure

### Breaking changes

**Imports:**
```python
# Old
from app.services.crypto import encrypt_snapshot

# New
from shared.crypto import encrypt_snapshot
```

**Running app:**
```bash
# Old
uv run uvicorn app.main:app --reload

# New
cd edge
uv run uvicorn app.main:app --reload
```

**Dependencies:**
```bash
# Old
uv sync  # Install all dependencies

# New
cd edge && uv sync  # Install Edge dependencies
cd hub && uv sync   # Install Hub dependencies
```

## Rationale
Monorepo tach biet Edge va Hub giup:
- **Bao mat:** Hub co quyen cao hon, Edge chi thay 1 tram
- **Deploy:** Build rieng, khong phai ship tat ca code
- **Dependencies:** Edge khong can duckdb, Hub khong can fastapi
- **Maintainability:** Code ro rang, de tim, de sua

Giu `shared/` giup DRY va nhat quan encryption giua Edge va Hub.

## Related Documents
- [18. Two-App Architecture: Edge vs Hub](18_Two_App_Architecture.md)
- [15. Hub Aggregation: DuckDB Analytics Pipeline](15_Hub_Aggregation.md)
- [07. Active Sync Protocol: The Encrypted SQLite Blob](07_active_sync_protocol.md)

## Quick Reference

### Edge App Location
```
edge/
├── app/          # FastAPI application
├── tests/        # Tests
└── pyproject.toml
```

See Edge code in `edge/app/` directory.

### Hub App Location
```
hub/
├── carevl_hub/   # CLI application
├── tests/        # Tests
└── pyproject.toml
```

See Hub code in `hub/carevl_hub/` directory.

### Shared Code Location
```
shared/
├── crypto.py     # Encryption/decryption
├── models.py     # Pydantic models
└── constants.py  # Constants
```

See shared code in `shared/` directory.
