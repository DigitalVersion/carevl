# Feature: QR Code Provisioning (Thẻ bài điện tử)

## Trạng thái (Status)
- [ ] Đã triển khai (Deployed)
- [ ] Đang phát triển (In Progress)
- [x] Kế hoạch (Planned)

## Mô tả Nghiệp vụ (Business Logic)
Thay vì bắt Site Operator gõ tay những chuỗi ký tự dài ngoằng (Token, Encryption Key, Site ID) dễ sai, Hub Admin có thể cấp quyền bằng "Thẻ bài điện tử" qua 2 phương thức:

### Công cụ quản lý Site Configuration
Hub Admin sử dụng Dashboard nội bộ hoặc CLI Script để tạo và quản lý thông số cho từng trạm/xã:

**Thông số cần tạo cho mỗi Site:**
1. **Site ID**: Định danh duy nhất theo format `{Tinh}_{Huyen}_{Ma}` 
   - Ví dụ: `VinhLong_LongHo_01`, `VinhLong_BinhMinh_02`
   - Quy tắc: Không dấu, PascalCase, kết thúc bằng số thứ tự

2. **GitHub Token (Fine-grained PAT)**: 
   - Scope: Write access vào repository `carevl-snapshots`
   - Expiration: 1 năm (có thể gia hạn)
   - Permissions: `contents: write`, `metadata: read`

3. **Encryption Key**: 
   - Chuỗi ngẫu nhiên mạnh 32 bytes (AES-256)
   - Generate bằng `secrets.token_bytes(32)` hoặc `openssl rand -base64 32`
   - Unique cho mỗi Site (không được trùng lặp)

4. **Site Name**: Tên đầy đủ của trạm (có dấu)
   - Ví dụ: "Trạm Y tế xã Long Hồ"

**Công cụ quản lý có 2 dạng:**

#### A. Dashboard Web UI (Khuyên dùng)
Hub Admin truy cập trang `/admin/sites` để:
- Xem danh sách tất cả Sites (bảng với filter, search, sort)
- Tạo Site mới qua form (tự động generate Token + Key)
- Xem chi tiết Site (Token, Key, QR Code)
- Tạo lại Token/Key khi cần
- Tạo QR Code cho Site
- Xem audit log (ai làm gì, khi nào)

**UI Features:**
- 📊 Dashboard tổng quan: Số lượng Sites, Sites active, QR codes đã tạo
- 🔍 Search & Filter: Tìm theo Site ID, tên, tỉnh, huyện
- 📋 Batch operations: Tạo nhiều Sites từ CSV
- 📥 Export: Xuất danh sách Sites ra CSV/Excel
- 🔐 Security: Chỉ Hub Admin có quyền truy cập

#### B. CLI Script (Cho automation)
Script `scripts/hub_admin_cli.py` để tạo và quản lý Sites qua command line.

### Phương thức cấp quyền cho Site Operator

### Cách A: QR Code (Chuyên nghiệp - Khuyên dùng)
1. **Hub Admin**: Truy cập Admin Panel, chọn "Tạo thẻ bài cho trạm mới"
2. **Hub Admin**: Nhập thông tin:
   - Site ID (VD: `TRAM_BINH_MINH`)
   - Site Name (VD: "Trạm Y tế Bình Minh")
   - Repository URL
3. **Hub Admin**: Hệ thống tự động:
   - Sinh GitHub Token với quyền phù hợp
   - Sinh Encryption Key (AES-256)
   - Đóng gói tất cả vào JSON
   - Tạo mã QR Code
4. **Hub Admin**: In hoặc gửi mã QR cho Site Operator
5. **Site Operator**: Khi chạy app lần đầu (bước Setup), chọn "Quét mã QR"
6. **Site Operator**: Dùng camera quét mã QR
7. **App**: Tự động điền tất cả thông tin vào `.env` và hoàn tất setup

### Cách B: Config File (Dự phòng)
1. **Hub Admin**: Xuất file `site_config.json` chứa thông tin tương tự
2. **Site Operator**: Copy file vào thư mục `config/`
3. **App**: Tự động đọc và import cấu hình

## Cấu trúc dữ liệu QR Code

```json
{
  "version": "1.0",
  "site_id": "TRAM_BINH_MINH",
  "site_name": "Trạm Y tế Bình Minh",
  "repository_url": "https://github.com/DigitalVersion/vinhlong-health-record",
  "github_token": "ghp_xxxxxxxxxxxxxxxxxxxx",
  "encryption_key": "base64_encoded_key_here",
  "hub_url": "https://hub.carevl.vn",
  "created_at": "2026-04-27T10:30:00Z",
  "expires_at": "2026-05-27T10:30:00Z"
}
```

## Bảo mật

### Mã hóa QR Code
- QR Code chứa dữ liệu nhạy cảm (Token, Key) nên phải được mã hóa
- Sử dụng **Symmetric Encryption** với Master Key của Hub
- Site Operator cần nhập **PIN Hub** (6 số) để giải mã QR Code
- PIN Hub được Hub Admin cung cấp riêng (qua điện thoại/SMS)

### Thời hạn QR Code
- Mỗi QR Code có thời hạn sử dụng (mặc định 30 ngày)
- Sau khi hết hạn, QR Code không thể sử dụng
- Hub Admin có thể thu hồi QR Code bất kỳ lúc nào

### Audit Log
- Mọi lần tạo QR Code đều được ghi log:
  - Ai tạo (Hub Admin username)
  - Khi nào tạo
  - Cho trạm nào
- Mọi lần sử dụng QR Code đều được ghi log:
  - Trạm nào sử dụng
  - Khi nào sử dụng
  - Địa chỉ IP (nếu có mạng)

## Các Endpoints liên quan (API/UI Routes)

### Hub Admin Dashboard (Web UI)
- `GET /admin/sites`: Danh sách tất cả các Site đã tạo
- `GET /admin/sites/create`: Form tạo Site mới
- `POST /admin/sites/create`: Xử lý tạo Site (auto-generate Token + Key)
- `GET /admin/sites/{site_id}`: Chi tiết Site (xem Token, Key, QR Code)
- `PUT /admin/sites/{site_id}`: Cập nhật thông tin Site
- `POST /admin/sites/{site_id}/regenerate-token`: Tạo lại GitHub Token
- `POST /admin/sites/{site_id}/regenerate-key`: Tạo lại Encryption Key
- `DELETE /admin/sites/{site_id}`: Xóa Site (cần xác nhận)

### Hub Admin Provisioning
- `GET /admin/provisioning`: Trang quản lý thẻ bài điện tử
- `POST /admin/provisioning/create`: Tạo QR Code mới cho trạm
- `GET /admin/provisioning/qr/{site_id}`: Xem/In QR Code
- `POST /admin/provisioning/revoke/{site_id}`: Thu hồi QR Code
- `GET /admin/provisioning/logs`: Xem audit log

### Site Setup
- `GET /setup/qr-scan`: Màn hình quét QR Code
- `POST /setup/qr-import`: Import config từ QR Code
- `POST /setup/file-import`: Import config từ file JSON

## UI/UX Flow

### Hub Admin Flow (Tạo Site mới)
```
[Admin Dashboard] 
  → [Sites Management]
  → [Create New Site]
  → [Form: Site ID, Site Name, Province, District]
  → [Submit]
  → [Hệ thống tự động:]
      - Generate GitHub Fine-grained PAT
      - Generate AES-256 Encryption Key
      - Lưu vào database
      - Hiển thị thông tin Site
  → [Generate QR Code]
  → [Nhập PIN Hub (6 số)]
  → [Hiển thị QR Code + PIN Hub]
  → [In/Lưu QR Code]
```

### Site Operator Flow
```
[Admin Panel] 
  → [Tạo thẻ bài mới]
  → [Nhập Site ID, Site Name]
  → [Hệ thống sinh Token + Key]
  → [Hiển thị QR Code + PIN Hub]
  → [In/Lưu QR Code]
```

### Site Operator Flow
```
[Chạy app lần đầu]
  → [Màn hình Setup]
  → [Chọn "Quét mã QR"]
  → [Nhập PIN Hub (6 số)]
  → [Quét QR Code bằng camera]
  → [Xác nhận thông tin]
  → [Hoàn tất setup]
```

## Technical Implementation

### Thư viện cần thiết
- **QR Code Generation**: `qrcode` (Python)
- **QR Code Scanning**: `html5-qrcode` (JavaScript - đã có)
- **Encryption**: `cryptography` (Python - đã có)

### Database Schema

#### Table: sites
```sql
CREATE TABLE sites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    site_id TEXT UNIQUE NOT NULL,           -- VinhLong_LongHo_01
    site_name TEXT NOT NULL,                -- Trạm Y tế xã Long Hồ
    province TEXT NOT NULL,                 -- Vĩnh Long
    district TEXT NOT NULL,                 -- Long Hồ
    github_token TEXT NOT NULL,             -- Fine-grained PAT
    encryption_key TEXT NOT NULL,           -- AES-256 key (base64)
    repository_url TEXT NOT NULL,           -- GitHub repo URL
    hub_url TEXT,                           -- Hub API URL
    created_by TEXT NOT NULL,               -- Admin username
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP,
    active BOOLEAN DEFAULT TRUE,
    notes TEXT                              -- Ghi chú nội bộ
);
```

#### Table: provisioning_tokens
```sql
CREATE TABLE provisioning_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    site_id TEXT NOT NULL,
    qr_code_hash TEXT UNIQUE NOT NULL,      -- SHA256 hash của QR content
    pin_hub TEXT NOT NULL,                  -- PIN Hub (encrypted)
    created_by TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    revoked BOOLEAN DEFAULT FALSE,
    revoked_at TIMESTAMP,
    revoked_by TEXT,
    used_at TIMESTAMP,
    used_by_ip TEXT,
    FOREIGN KEY (site_id) REFERENCES sites(site_id)
);
```

#### Table: site_audit_log
```sql
CREATE TABLE site_audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    site_id TEXT NOT NULL,
    action TEXT NOT NULL,                   -- CREATE, UPDATE, DELETE, REGENERATE_TOKEN, etc.
    performed_by TEXT NOT NULL,
    performed_at TIMESTAMP NOT NULL,
    details TEXT,                           -- JSON với thông tin chi tiết
    ip_address TEXT,
    FOREIGN KEY (site_id) REFERENCES sites(site_id)
);
```

## Lợi ích

### Cho Hub Admin
- ✅ Không cần gửi Token/Key qua email/chat (rủi ro bảo mật)
- ✅ Kiểm soát được thời hạn và thu hồi
- ✅ Audit log đầy đủ
- ✅ Tạo hàng loạt cho nhiều trạm

### Cho Site Operator
- ✅ Không cần gõ tay chuỗi dài (giảm sai sót)
- ✅ Setup nhanh chóng (< 1 phút)
- ✅ Không cần kiến thức kỹ thuật
- ✅ Có thể setup offline (sau khi quét QR)

## Persona Impact
- **Hub Admin**: Tạo và quản lý QR Code
- **Site Operator**: Quét QR Code để setup trạm

## CLI Script Alternative

Ngoài Dashboard, Hub Admin có thể dùng CLI script để quản lý nhanh:

### Script: `scripts/hub_admin_cli.py`

```python
# Tạo Site mới
python scripts/hub_admin_cli.py create-site \
    --site-id VinhLong_LongHo_01 \
    --site-name "Trạm Y tế xã Long Hồ" \
    --province "Vĩnh Long" \
    --district "Long Hồ"

# Tạo QR Code cho Site
python scripts/hub_admin_cli.py generate-qr \
    --site-id VinhLong_LongHo_01 \
    --output qr_codes/VinhLong_LongHo_01.png

# Liệt kê tất cả Sites
python scripts/hub_admin_cli.py list-sites

# Xem chi tiết Site
python scripts/hub_admin_cli.py show-site \
    --site-id VinhLong_LongHo_01

# Tạo lại Token
python scripts/hub_admin_cli.py regenerate-token \
    --site-id VinhLong_LongHo_01

# Thu hồi QR Code
python scripts/hub_admin_cli.py revoke-qr \
    --site-id VinhLong_LongHo_01

# Export tất cả Sites ra CSV
python scripts/hub_admin_cli.py export-sites \
    --output sites_export.csv
```

### Script Features
- ✅ Auto-generate GitHub Fine-grained PAT (qua GitHub API)
- ✅ Auto-generate Encryption Key (cryptographically secure)
- ✅ Validate Site ID format
- ✅ Check duplicate Site ID
- ✅ Batch create multiple Sites từ CSV
- ✅ Export/Import Site configurations

## Danh sách ảnh Mockup
- `admin_sites_list.png`: Danh sách tất cả Sites (Dashboard)
- `admin_site_create.png`: Form tạo Site mới
- `admin_site_detail.png`: Chi tiết Site (Token, Key, QR Code)
- `admin_qr_create.png`: Màn hình tạo QR Code (Hub Admin)
- `admin_qr_display.png`: Hiển thị QR Code + PIN Hub
- `site_qr_scan.png`: Màn hình quét QR Code (Site Operator)
- `site_qr_confirm.png`: Xác nhận thông tin sau khi quét

## Lịch sử thay đổi (Changelog)
- **2026-04-27**: Kiro - Tạo tài liệu kế hoạch cho tính năng QR Provisioning

## Related Documents
- [Auth Gateway](auth_gateway.md)
- [Bootstrap Infrastructure](../ACTIVE/14_Bootstrap_Infrastructure.md)
- [SQLite Security](../ACTIVE/02_SQLite_Security.md)
