# Two-App Architecture: Edge vs Hub

## Status
**[Active - Planned]**

**Last Updated**: 2026-04-28

## Context

Hệ thống CareVL có 2 nhóm user hoàn toàn khác nhau:
1. **Edge (Trạm):** Operator, Bác sĩ, Lab Tech, Trưởng trạm - Nhập liệu hàng ngày
2. **Hub (Tỉnh):** Admin Hub, Analyst - Tổng hợp báo cáo từ 100 trạm

**Vấn đề nếu gom chung 1 app:**
- ❌ Code khổng lồ (1 triệu dòng), khó maintain
- ❌ Dependencies conflict (Edge cần HTMX, Hub cần DuckDB/Jupyter)
- ❌ Deployment phức tạp (Edge cần .exe, Hub cần Python env)
- ❌ Security risk (Hub có quyền cao hơn, không nên chạy trên máy trạm)

## Decision

**Phát triển 2 app trong 1 monorepo với cấu trúc rõ ràng:**

### 1. CareVL Edge (Station App)

**Mục đích:** Quản lý dữ liệu tại trạm y tế

**Tech Stack:**
- FastAPI (backend)
- SQLite (database)
- HTMX + Alpine.js + TailwindCSS (frontend)
- PyInstaller (đóng gói .exe)

**Features:**
- Gateway Setup (Invite Code authentication)
- 10 chức năng sidebar (Tiếp nhận → Cài đặt)
- Active Sync (upload snapshot lên GitHub Releases)
- Offline-first (PIN authentication)

**Deployment:**
- Windows .exe (single file)
- Chạy local tại trạm
- Không cần internet (trừ khi sync)

**Codebase size:** ~10,000-20,000 dòng

**Location:** `edge/` folder trong monorepo

---

### 2. CareVL Hub (Analytics App)

**Mục đích:** Tổng hợp và phân tích dữ liệu từ tất cả trạm

**Tech Stack:**
- Python CLI (typer/click)
- DuckDB (analytical database)
- Pandas (data processing)
- Jupyter Notebook (ad-hoc analysis)
- Streamlit/Dash (optional: web dashboard)

**Features:**
- Download snapshots từ 100 repos (GitHub API)
- Decrypt snapshots (AES-256)
- Aggregate data (DuckDB queries)
- Generate reports (Excel, PDF, Parquet)
- Data quality checks
- Audit logs

**Deployment:**
- Python package (pip install)
- Chạy trên máy Admin Hub (Windows/Linux)
- Cần internet (download snapshots)

**Codebase size:** ~5,000-10,000 dòng

**Location:** `hub/` folder trong monorepo

**Authentication:**
- Hub app đăng nhập bằng **GitHub Classic PAT** của chủ tổ chức (organization owner)
- Cần `repo` scope để access tất cả repos của các trạm
- Hoặc dùng **GitHub App** với quyền read releases từ organization

## Architecture Diagrams

### Ecosystem Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    CareVL Ecosystem                         │
└─────────────────────────────────────────────────────────────┘

┌──────────────────────┐                  ┌──────────────────────┐
│   CareVL Edge App    │                  │   CareVL Hub App     │
│   (Station 001)      │                  │   (Admin Hub)        │
├──────────────────────┤                  ├──────────────────────┤
│ • FastAPI + SQLite   │                  │ • Python CLI         │
│ • HTMX UI            │                  │ • DuckDB             │
│ • Offline-first      │                  │ • Jupyter            │
│ • Windows .exe       │                  │ • Streamlit          │
└──────────┬───────────┘                  └──────────┬───────────┘
           │                                         │
           │ Upload snapshot                         │ Download all
           │ (GitHub Releases)                       │ snapshots
           │                                         │
           ▼                                         ▼
    ┌─────────────────────────────────────────────────────┐
    │           GitHub (Data Transport Layer)             │
    ├─────────────────────────────────────────────────────┤
    │  • station-001 repo → Releases (snapshots)          │
    │  • station-002 repo → Releases (snapshots)          │
    │  • ... (100 repos)                                  │
    └─────────────────────────────────────────────────────┘

┌──────────────────────┐     ┌──────────────────────┐
│   CareVL Edge App    │     │   CareVL Edge App    │
│   (Station 002)      │ ... │   (Station 100)      │
└──────────────────────┘     └──────────────────────┘
```

### Edge App Architecture (Station)

![Edge App Architecture](../ASSETS/edge_app_architecture.svg)

**Layers:**
- **User Layer:** Operator, Clinician, Lab Tech (Browser-based)
- **Frontend:** HTMX (dynamic UI) + Alpine.js (state) + TailwindCSS (styling)
- **Backend:** FastAPI routes (UI, API, Auth, Admin)
- **Data:** SQLite + SQLAlchemy ORM
- **Services:** Crypto (AES-256) + GitHub Sync (upload snapshots)

### Hub App Architecture (Analytics)

![Hub App Architecture](../ASSETS/hub_app_architecture.svg)

**Pipeline:**
1. **CLI Layer:** Typer commands (init, download, aggregate, report, dashboard)
2. **Data Pipeline:**
   - GitHub Downloader (org-level PAT, 100 repos)
   - Crypto Service (decrypt snapshots)
   - DuckDB Aggregator (JOIN queries, stats)
   - Report Generator (Excel, PDF, charts)
3. **Analytics:** Jupyter Notebooks, Streamlit Dashboard, Pandas
4. **Output:** Excel, PDF, Parquet, Email alerts

## Communication Protocol

**Edge → Hub (One-way, async):**
1. Edge app tạo snapshot (SQLite encrypted)
2. Upload lên GitHub Releases của repo riêng
3. Hub app định kỳ (hoặc on-demand) download tất cả snapshots
4. Hub aggregate và tạo báo cáo

**Không có real-time sync!** Hub chỉ pull data khi cần.

## Monorepo Structure

```
carevl/  (root repo: DigitalVersion/carevl)
├── edge/                    # Edge App (Station)
│   ├── app/
│   │   ├── api/            # FastAPI routes
│   │   ├── core/           # Config, database
│   │   ├── models/         # SQLAlchemy models
│   │   ├── services/       # Business logic
│   │   ├── templates/      # Jinja2 HTML
│   │   └── static/         # CSS, JS
│   ├── tests/              # Pytest for Edge
│   ├── carevl.spec         # PyInstaller config
│   ├── pyproject.toml      # Edge dependencies
│   └── README.md
│
├── hub/                     # Hub App (Analytics)
│   ├── carevl_hub/
│   │   ├── cli.py          # Typer CLI commands
│   │   ├── downloader.py   # GitHub API client (org-level PAT)
│   │   ├── crypto.py       # Decrypt snapshots
│   │   ├── aggregator.py   # DuckDB queries
│   │   ├── reports.py      # Generate reports
│   │   └── config.py       # Hub config
│   ├── notebooks/          # Jupyter notebooks
│   ├── tests/              # Pytest for Hub
│   ├── pyproject.toml      # Hub dependencies
│   └── README.md
│
├── shared/                  # Shared code between Edge & Hub
│   ├── crypto.py           # Common encryption/decryption
│   ├── models.py           # Common data models
│   ├── constants.py        # Shared constants
│   └── __init__.py
│
├── scripts/                 # Build & deployment scripts
│   ├── build_edge.sh       # Build Edge .exe
│   ├── build_hub.sh        # Package Hub CLI
│   └── bootstrap.py        # One-liner setup
│
├── AGENTS/                  # Documentation (ADR)
├── config/                  # Config files
├── data/                    # Local data (Edge only)
├── legacy/                  # Legacy Tkinter app
├── .github/                 # CI/CD workflows
│   └── workflows/
│       ├── build-edge.yml  # Build Edge .exe
│       └── test-hub.yml    # Test Hub CLI
├── .gitignore
├── README.md               # Root README
└── TUTORIAL.md             # User guide

```

### Dependencies

**Edge (`edge/pyproject.toml`):**
- fastapi
- sqlalchemy
- cryptography
- httpx (GitHub API)
- jinja2
- uvicorn

**Hub (`hub/pyproject.toml`):**
- typer
- duckdb
- pandas
- httpx (GitHub API - org-level)
- cryptography
- openpyxl (Excel export)
- streamlit (optional)

**Shared:**
- cryptography (used by both)
- pydantic (data validation)

## CLI Commands (Hub App)

```bash
# Setup
uv run carevl-hub init --encryption-key "xxx"

# Download snapshots from all stations
uv run carevl-hub download --date 2026-04-28

# Decrypt all snapshots
uv run carevl-hub decrypt --input snapshots/ --output decrypted/

# Aggregate data
uv run carevl-hub aggregate --output hub_report.parquet

# Generate Excel report
uv run carevl-hub report --format excel --output monthly_report.xlsx

# Launch web dashboard
uv run carevl-hub dashboard --port 8080
```

## Development Workflow

### Edge App (Trạm)
```bash
# Development
cd edge
uv sync
uv run uvicorn app.main:app --reload

# Build .exe
cd ..
uv run pyinstaller edge/carevl.spec

# Test
cd edge
uv run pytest
```

### Hub App (Tỉnh)
```bash
# Development
cd hub
uv sync
uv run python -m carevl_hub.cli --help

# Install as package (editable mode)
cd hub
uv pip install -e .

# Test
uv run pytest
```

### Shared Code
```bash
# Import shared code in Edge
from shared.crypto import encrypt_snapshot

# Import shared code in Hub
from shared.crypto import decrypt_snapshot
```

## Deployment

### Edge App
1. Build `carevl.exe` bằng PyInstaller: `./scripts/build_edge.sh`
2. Upload lên GitHub Releases của `DigitalVersion/carevl`
3. Trạm download và chạy (hoặc dùng Bootstrap script)

### Hub App
1. Package Hub CLI: `./scripts/build_hub.sh`
2. Publish lên PyPI (optional): `cd hub && uv publish`
3. Admin Hub install:
   - Từ PyPI: `uv pip install carevl-hub`
   - Từ source (dev mode): `cd hub && uv pip install -e .`
4. Config encryption key và GitHub PAT (organization owner)
5. Chạy CLI commands: `uv run carevl-hub download --date 2026-04-28`

## Security Separation

| Aspect | Edge App | Hub App |
|--------|----------|---------|
| **GitHub Access** | 1 repo (Fine-grained PAT) | All org repos (Classic PAT - org owner) |
| **Encryption Key** | Không có (chỉ encrypt) | Có (decrypt tất cả) |
| **Data Access** | 1 trạm | Tất cả trạm |
| **User Level** | Operator, Clinician | Admin Hub, Analyst |
| **Network** | Offline-first | Online-required |
| **Location** | `edge/` folder | `hub/` folder |

**Lợi ích:**
- Edge app bị compromise → Chỉ mất 1 trạm
- Hub app bị compromise → Mất tất cả (nhưng chỉ chạy trên máy Admin được bảo vệ)
- Shared code giúp đồng bộ logic encryption/decryption

## Migration Path

**Hiện tại:** Tất cả code trong root của repo `DigitalVersion/carevl`

**Bước 1: Tạo cấu trúc monorepo**
```bash
# Tạo folders
mkdir -p edge hub shared scripts

# Di chuyển Edge code
mv app edge/
mv carevl.spec edge/
mv pyproject.toml edge/

# Tạo Hub structure
mkdir -p hub/carevl_hub hub/notebooks hub/tests
touch hub/carevl_hub/cli.py
touch hub/pyproject.toml

# Tạo Shared code
touch shared/crypto.py shared/models.py shared/__init__.py
```

**Bước 2: Extract shared code**
```bash
# Di chuyển crypto logic từ Edge sang Shared
# app/services/crypto.py → shared/crypto.py

# Update imports trong Edge
# from app.services.crypto import encrypt → from shared.crypto import encrypt
```

**Bước 3: Setup Hub app**
```bash
cd hub
# Tạo CLI với Typer
# Implement DuckDB aggregation
# Add Jupyter notebooks
```

**Bước 4: Update CI/CD**
```bash
# .github/workflows/build-edge.yml
# .github/workflows/test-hub.yml
```

**Bước 5: Documentation**
```bash
# edge/README.md - Hướng dẫn cho Operator
# hub/README.md - Hướng dẫn cho Admin Hub
# README.md (root) - Overview toàn bộ monorepo
```

## Rationale

### Tại sao chọn Monorepo?

1. **Code Reuse:**
   - Shared crypto logic (encrypt/decrypt)
   - Common data models (Patient, Encounter)
   - Không cần duplicate code

2. **Synchronized Development:**
   - Refactor cả Edge và Hub cùng lúc
   - Version control đồng bộ
   - Dễ test integration

3. **Simplified CI/CD:**
   - 1 GitHub Actions workflow
   - Build cả Edge .exe và Hub package
   - Test cả 2 apps trong 1 pipeline

4. **Documentation Centralized:**
   - AGENTS/ folder chứa tất cả ADR
   - Dễ tìm kiếm và maintain
   - Single source of truth

5. **Team Collaboration:**
   - Team nhỏ (1-3 người) dễ collaborate
   - Không cần sync giữa 2 repos
   - Pull request review cả 2 apps

### Tại sao không tách 2 repos?

- ❌ Duplicate shared code (crypto, models)
- ❌ Khó đồng bộ version
- ❌ CI/CD phức tạp hơn (2 repos, 2 workflows)
- ✅ Monorepo với structure rõ ràng đủ tốt

### Tại sao không microservices?

- ❌ Không cần real-time communication
- ❌ Không có ngân sách cho server
- ✅ Async via GitHub Releases đủ tốt
- ✅ Đơn giản hơn, dễ deploy hơn

### Khi nào nên tách repos?

Chỉ tách khi:
- Team lớn (>5 người)
- Edge và Hub develop hoàn toàn độc lập
- Cần release cycle khác nhau
- Có nhiều conflicts về dependencies

## Related Documents
- [01. FastAPI Core Architecture](01_FastAPI_Core.md) - Edge app
- [15. Hub Aggregation: DuckDB Analytics Pipeline](15_Hub_Aggregation.md) - Hub app
- [17. Invite Code Authentication](17_Invite_Code_Authentication.md) - Edge setup

## Next Steps

- [ ] Tạo cấu trúc monorepo (`edge/`, `hub/`, `shared/`)
- [ ] Di chuyển Edge code vào `edge/` folder
- [ ] Extract shared crypto logic vào `shared/`
- [ ] Tạo Hub CLI với Typer trong `hub/`
- [ ] Implement DuckDB aggregation
- [ ] Setup GitHub org-level PAT cho Hub
- [ ] Viết `scripts/build_edge.sh` và `scripts/build_hub.sh`
- [ ] Update CI/CD workflows
- [ ] Viết `edge/README.md` và `hub/README.md`
- [x] Vẽ sơ đồ Edge App architecture
- [x] Vẽ sơ đồ Hub App architecture

