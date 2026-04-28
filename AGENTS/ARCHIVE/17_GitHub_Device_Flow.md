# GitHub Device Flow Authentication (DEPRECATED)

## Status
**[Deprecated]** - Replaced by Invite Code Authentication (Fine-grained PAT)

**Deprecated Date**: 2026-04-28

## Lý do Deprecated

Phương thức Device Flow đã được thay thế bởi **Invite Code Authentication** sử dụng Fine-grained Personal Access Token.

### Vấn đề với Device Flow:

1. **Phức tạp cho người dùng:**
   - Bước 1: Quét QR code trên điện thoại
   - Bước 2: Nhập device code vào GitHub
   - Bước 3: Nhập repo URL thủ công
   - Bước 4: Accept invite link (nếu chưa có quyền)
   - Bước 5: Chờ admin approve
   - → Tổng cộng 5 bước, mất 10-15 phút

2. **Yêu cầu GitHub account cá nhân:**
   - Mỗi người dùng cần có GitHub account
   - Cần training về GitHub
   - Khó quản lý khi nhân viên thay đổi

3. **Token management phức tạp:**
   - Token expire sau 8 giờ
   - Cần implement refresh token logic
   - Cần handle token expiration gracefully

4. **Không phù hợp với constraint:**
   - Hệ thống không có server để handle OAuth callback
   - Người dùng cuối không có kỹ năng kỹ thuật
   - Cần giải pháp đơn giản hơn

### Giải pháp thay thế (Invite Code):

1. **Đơn giản hơn:**
   - Hub Admin generate invite code (1 lần)
   - Trạm paste code vào input field
   - App tự động setup
   - → Chỉ 1 bước, mất 2 phút

2. **Không cần GitHub account:**
   - Trạm không cần biết gì về GitHub
   - Chỉ cần paste code

3. **Không expire:**
   - Fine-grained PAT có thể set "no expiration"
   - Không cần refresh logic

4. **Phù hợp constraint:**
   - Không cần server
   - Không cần kỹ năng kỹ thuật
   - Miễn phí 100%

## Tài liệu gốc (Device Flow)

### Quy trình 5 bước (Device Flow - DEPRECATED)

1. **Xác thực thiết bị bằng GitHub Device Flow**
   - App hiển thị device code
   - User quét QR trên điện thoại
   - Nhập code vào github.com/login/device
   - GitHub trả về access token

2. **Cấu hình URL của Repository đích**
   - User nhập repo URL thủ công
   - VD: `DigitalVersion/carevl-data`

3. **Kiểm tra quyền Ghi (Write)**
   - App check xem user có write access không
   - Nếu không: Hiển thị QR invite link
   - Admin Hub quét QR để invite user
   - User accept invite qua email

4. **Khởi tạo Database**
   - Tạo DB trống (trạm mới)
   - Hoặc Restore DB snapshot (cài lại máy)

5. **Thiết lập mã PIN 6 số**
   - Encrypt token với PIN
   - Dùng PIN để unlock app offline

### Endpoints (Device Flow - DEPRECATED)

- `GET /login`: Hiển thị device code và QR
- `GET/POST /setup/repo`: Nhập repo URL
- `GET/POST /setup/permission`: Check quyền và hiển thị invite QR
- `GET/POST /setup/data`: New/Restore DB
- `GET/POST /setup/pin`: Setup PIN

### Code Reference (Device Flow - DEPRECATED)

```python
# app/api/auth_routes.py (OLD)
from fastapi import APIRouter
import requests

router = APIRouter()

@router.get("/login")
async def github_device_flow():
    # Request device code
    response = requests.post(
        "https://github.com/login/device/code",
        data={
            "client_id": GITHUB_CLIENT_ID,
            "scope": "repo"
        }
    )
    
    data = response.json()
    return {
        "device_code": data["device_code"],
        "user_code": data["user_code"],
        "verification_uri": data["verification_uri"],
        "expires_in": data["expires_in"]
    }

@router.post("/setup/repo")
async def setup_repo(repo_url: str):
    # Validate repo URL
    # Check write access
    # ...
    pass
```

## Migration Path

Nếu đã implement Device Flow, migrate sang Invite Code:

1. **Hub Admin:**
   - Generate Fine-grained PATs cho tất cả trạm
   - Export invite codes
   - Gửi codes cho trạm

2. **Station App:**
   - Thay endpoint `/login` bằng `/setup/invite-code`
   - Remove device flow logic
   - Add invite code parsing
   - Update git operations để dùng PAT thay vì OAuth token

3. **Database:**
   - Migrate `github_token` → `pat_token`
   - Update credential storage

## Related Documents

- [17. Invite Code Authentication (NEW)](../ACTIVE/17_Invite_Code_Authentication.md) - Phương thức mới thay thế
- [01. FastAPI Core Architecture](../ACTIVE/01_FastAPI_Core.md)
- [02. SQLite Security](../ACTIVE/02_SQLite_Security.md)

## Changelog

- **2026-04-27**: Jules - Khởi tạo quy trình Gateway 5 bước Device Flow
- **2026-04-28**: Kiro - Deprecated, thay thế bởi Invite Code Authentication

