# Tổng quan dự án & Quy ước branch

## Tổng quan dự án

**CareVL** (Care Vinh Long) là ứng dụng desktop quản lý hồ sơ khám sức khỏe cho tỉnh Vĩnh Long. (Note: Project is currently migrating to a FastAPI web architecture).

- **Stack**: Python 3.11+, FastAPI, CustomTkinter (legacy), SQLite local, Git sync, DuckDB cho Hub
- **Nền tảng**: Windows, offline-first
- **Xác thực**: GitHub OAuth Device Flow

## Quy ước branch

- `main` là nhánh chính, luôn ưu tiên giữ ở trạng thái ổn định để sử dụng thật.
- `canary` là nhánh phát triển tích lũy hằng ngày giữa mình và agent.
- Tính năng mới, refactor, sửa lỗi không khẩn cấp: làm trên `canary`.
- Khi đã test ổn trên `canary`, mới gộp vào `main`.
- Nếu có hotfix cần sửa trực tiếp trên `main`, phải gộp ngược lại sang `canary` sớm để tránh lệch nhánh.
