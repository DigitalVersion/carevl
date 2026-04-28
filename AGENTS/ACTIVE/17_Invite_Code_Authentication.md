# Invite Code Authentication: Fine-grained PAT Provisioning

## Status
**[Active - Planned]**

**Last Updated**: 2026-04-28

## Context

Hệ thống CareVL cần phương thức xác thực đơn giản cho trạm y tế mà:
- Không cần server backend
- Không cần kỹ năng kỹ thuật từ người dùng
- Chỉ dựa vào GitHub (miễn phí)
- Bảo mật đủ tốt cho use case y tế cộng đồng

**Constraint:**
- Không có ngân sách cho server/infrastructure
- Người dùng cuối không biết Git, GitHub, OAuth
- Cần setup trong 5 phút

## Decision

Sử dụng **GitHub Fine-grained Personal Access Token (PAT)** với Invite Code provisioning.

### Kiến trúc

```
Hub Admin (1 lần)          Trạm (tự làm)
─────────────────          ─────────────
1. Tạo bot account         1. Nhập Invite Code
2. Tạo 100 repos              ↓
3. Generate 100 PATs       2. App parse code
4. Export Invite Codes        ↓
5. Gửi qua Zalo/Email      3. Lưu PAT vào Credential Manager
                              ↓
                           4. Git clone/pull với PAT
                              ↓
                           5. Setup PIN
                              ↓
                           READY
```

## Technical Implementation

### Hub Admin Workflow

#### 1. Tạo Bot Account
```bash
# Tạo GitHub account thủ công
# Username: carevl-bot
# Email: carevl-bot@example.com
```

#### 2. Tạo Repositories
```python
# Script: scripts/hub_setup_repos.py
import requests

GITHUB_TOKEN = "ghp_xxxxx"  # Bot account PAT (classic, full repo access)
ORG_OR_USER = "carevl-bot"
REPO_PREFIX = "station"

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

for i in range(1, 101):
    repo_name = f"{REPO_PREFIX}-{i:03d}"
    data = {
        "name": repo_name,
        "private": True,
        "description": f"CareVL Station {i:03d} Data Repository",
        "auto_init": True  # Tạo với README.md
    }
    
    response = requests.post(
        f"https://api.github.com/user/repos",
        headers=headers,
        json=data
    )
    
    if response.status_code == 201:
        print(f"✓ Created {repo_name}")
    else:
        print(f"✗ Failed {repo_name}: {response.json()}")
```

#### 3. Generate Fine-grained PATs

**Không thể tạo qua API!** Fine-grained PAT phải tạo thủ công qua GitHub UI.

**Quy trình:**
1. Vào https://github.com/settings/personal-access-tokens/new
2. Điền thông tin:
   - **Token name**: `Station 001 Access`
   - **Expiration**: `No expiration`
   - **Repository access**: `Only select repositories` → Chọn `station-001`
   - **Permissions**:
     - Repository permissions:
       - `Contents`: Read and write
       - `Metadata`: Read-only (mandatory)
3. Click `Generate token`
4. Copy token: `github_pat_xxxxx...`
5. Lưu vào CSV

**Script hỗ trợ (semi-automated):**
```python
# Script: scripts/hub_generate_pat_csv.py
import csv

# Sau khi tạo PAT thủ công, paste vào đây
PATS = {
    "station-001": "github_pat_11AAAA...",
    "station-002": "github_pat_11BBBB...",
    # ... paste 100 tokens
}

with open("invite_codes.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["station_id", "station_name", "repo_url", "pat_token"])
    
    for station_id, pat in PATS.items():
        station_num = station_id.split("-")[1]
        writer.writerow([
            station_id,
            f"Trạm Y Tế {station_num}",
            f"https://github.com/carevl-bot/{station_id}.git",
            pat
        ])

print("✓ Generated invite_codes.csv")
```

#### 4. Generate Invite Codes

Invite Code = Base64 encode của JSON:
```python
# Script: scripts/hub_generate_invite_codes.py
import csv
import json
import base64

with open("invite_codes.csv", "r") as f:
    reader = csv.DictReader(f)
    
    for row in reader:
        invite_data = {
            "station_id": row["station_id"],
            "station_name": row["station_name"],
            "repo_url": row["repo_url"],
            "pat": row["pat_token"]
        }
        
        # Encode to base64
        json_str = json.dumps(invite_data)
        invite_code = base64.b64encode(json_str.encode()).decode()
        
        print(f"\n=== {row['station_name']} ===")
        print(f"Invite Code:")
        print(invite_code)
        print(f"\nGửi code này cho trạm qua Zalo/Email")
        print("=" * 50)
```

**Invite Code format:**
```
eyJzdGF0aW9uX2lkIjogInN0YXRpb24tMDAxIiwgInN0YXRpb25fbmFtZSI6ICJUcuG6oW0gWSBU4bq/IDAwMSIsICJyZXBvX3VybCI6ICJodHRwczovL2dpdGh1Yi5jb20vY2FyZXZsLWJvdC9zdGF0aW9uLTAwMS5naXQiLCAicGF0IjogImdpdGh1Yl9wYXRfMTFBQUFBLi4uIn0=
```

### Station Setup Workflow

#### 1. Nhập Invite Code (UI)

```python
# app/api/auth_routes.py
from fastapi import APIRouter, Form
import base64
import json

router = APIRouter()

@router.post("/setup/invite-code")
async def setup_invite_code(invite_code: str = Form(...)):
    try:
        # Decode base64
        json_str = base64.b64decode(invite_code).decode()
        data = json.loads(json_str)
        
        # Validate
        required_keys = ["station_id", "station_name", "repo_url", "pat"]
        if not all(k in data for k in required_keys):
            return {"error": "Invalid invite code format"}
        
        # Lưu vào session
        session["invite_data"] = data
        
        return {
            "success": True,
            "station_name": data["station_name"],
            "station_id": data["station_id"]
        }
    except Exception as e:
        return {"error": f"Invalid invite code: {str(e)}"}
```

#### 2. Lưu PAT vào Secure Storage

```python
# app/services/credential_manager.py
import keyring

SERVICE_NAME = "CareVL"

def store_pat(station_id: str, pat: str):
    """Lưu PAT vào Windows Credential Manager"""
    keyring.set_password(SERVICE_NAME, f"{station_id}_pat", pat)

def get_pat(station_id: str) -> str:
    """Lấy PAT từ Windows Credential Manager"""
    return keyring.get_password(SERVICE_NAME, f"{station_id}_pat")

def delete_pat(station_id: str):
    """Xóa PAT (khi revoke)"""
    keyring.delete_password(SERVICE_NAME, f"{station_id}_pat")
```

#### 3. Git Operations với PAT

```python
# app/services/github_sync.py
import subprocess
from app.services.credential_manager import get_pat

def git_clone_with_pat(repo_url: str, station_id: str, target_dir: str):
    """Clone repo sử dụng PAT"""
    pat = get_pat(station_id)
    
    # Inject PAT vào URL
    # https://github.com/user/repo.git
    # → https://oauth2:TOKEN@github.com/user/repo.git
    auth_url = repo_url.replace(
        "https://github.com/",
        f"https://oauth2:{pat}@github.com/"
    )
    
    result = subprocess.run(
        ["git", "clone", auth_url, target_dir],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        raise Exception(f"Git clone failed: {result.stderr}")
    
    return True

def git_push_with_pat(station_id: str, repo_dir: str):
    """Push changes sử dụng PAT"""
    pat = get_pat(station_id)
    
    # Set credential helper
    subprocess.run(
        ["git", "config", "credential.helper", "store"],
        cwd=repo_dir
    )
    
    # Push (Git sẽ dùng PAT từ credential helper)
    result = subprocess.run(
        ["git", "push", "origin", "main"],
        cwd=repo_dir,
        capture_output=True,
        text=True,
        env={"GIT_ASKPASS": "echo", "GIT_USERNAME": "oauth2", "GIT_PASSWORD": pat}
    )
    
    if result.returncode != 0:
        raise Exception(f"Git push failed: {result.stderr}")
    
    return True
```

## Security Analysis

### Threat Model

| Threat | Impact | Mitigation |
|--------|--------|------------|
| PAT lộ qua Zalo/Email | Attacker có thể đọc/ghi repo của 1 trạm | - Mỗi PAT chỉ scope 1 repo<br>- Gửi qua Zalo riêng tư<br>- Xóa tin nhắn sau khi setup<br>- Hub có thể revoke PAT ngay |
| PAT bị đánh cắp từ máy trạm | Attacker clone được dữ liệu 1 trạm | - PAT lưu trong Windows Credential Manager (encrypted)<br>- Cần physical access hoặc malware<br>- Thiệt hại giới hạn ở 1 trạm |
| Bot account bị compromise | Attacker có thể tạo/xóa PAT | - Bot account dùng 2FA<br>- Chỉ Hub Admin có password<br>- Monitor GitHub audit log |
| Man-in-the-middle | Attacker chặn PAT khi git push/pull | - Git dùng HTTPS (TLS encrypted)<br>- PAT không bao giờ gửi plaintext |

### Trade-offs Chấp Nhận

✅ **Ưu điểm:**
- Zero infrastructure cost
- Setup trong 5 phút
- Không cần kỹ năng kỹ thuật
- PAT không expire (no maintenance)

⚠️ **Nhược điểm:**
- PAT lộ → 1 trạm bị compromise (chấp nhận được)
- Phải tạo PAT thủ công (100 lần, 1 lần duy nhất)
- Không có audit log chi tiết (chỉ có GitHub audit)

## Rationale

### Tại sao không dùng GitHub App?
- ❌ Cần server để handle OAuth callback
- ❌ Phức tạp hơn cho người dùng (install app, authorize)
- ❌ Cần maintain app credentials

### Tại sao không dùng Device Flow?
- ❌ Cần user có GitHub account
- ❌ Phức tạp: Quét QR → Nhập code → Accept invite
- ❌ Token expire sau 8 giờ, cần refresh logic

### Tại sao Fine-grained PAT?
- ✅ Scope per repository (bảo mật tốt hơn classic PAT)
- ✅ Không cần server
- ✅ Không expire (set "no expiration")
- ✅ Miễn phí 100%
- ✅ UX đơn giản: Copy-paste code

## Implementation Checklist

### Hub Admin (One-time setup)
- [ ] Tạo GitHub bot account với 2FA
- [ ] Tạo 100 private repositories
- [ ] Generate 100 Fine-grained PATs (thủ công qua UI)
- [ ] Export invite codes (script)
- [ ] Gửi invite codes cho trạm qua Zalo/Email

### Station App (Development)
- [ ] UI: Input field cho Invite Code
- [ ] Backend: Parse và validate invite code
- [ ] Credential Manager: Lưu PAT vào Windows Credential Manager
- [ ] Git Service: Clone/pull/push với PAT authentication
- [ ] Setup flow: New DB / Restore DB
- [ ] PIN setup: Encrypt local token với PIN

### Testing
- [ ] Test invite code parsing
- [ ] Test PAT storage/retrieval
- [ ] Test git clone với PAT
- [ ] Test git push với PAT
- [ ] Test revoke PAT (Hub side)
- [ ] Test invalid/expired PAT handling

## Related Documents
- [01. FastAPI Core Architecture](01_FastAPI_Core.md)
- [02. SQLite Security & Snapshots](02_SQLite_Security.md)
- [07. Active Sync Protocol](07_active_sync_protocol.md)

## Migration from Device Flow

Tài liệu cũ về Device Flow đã được di chuyển vào ARCHIVE:
- [ARCHIVE: GitHub Device Flow Authentication](../ARCHIVE/17_GitHub_Device_Flow.md)

**Lý do thay đổi:**
- Device Flow phức tạp hơn cho người dùng (3 bước: QR → Code → Accept invite)
- Cần user có GitHub account cá nhân
- Token expire và cần refresh logic
- Fine-grained PAT đơn giản hơn (1 bước: Paste code) và phù hợp hơn với constraint "không có server"

