# 30. Hub Auto-Provisioning: Admin PAT + SSH Deploy Key

## Status
[Active - Implemented]

## Context

Mục tiêu: Hub Admin bấm nút trong GUI → tạo trạm mới tự động → có invite code gửi cho trạm.

**Giới hạn cứng của GitHub API:**
- ✅ Tạo repo qua API → được (Classic PAT, scope `repo`)
- ✅ Tạo deploy key cho repo qua API → được
- ❌ Tạo PAT qua API → không được (GitHub khoá từ 2020)

**Phân biệt người dùng:**
- **Hub Admin**: người kỹ thuật, tạo PAT 1 lần, dùng Hub GUI
- **Edge User**: y tá tại trạm, chỉ dán invite code vào app

## Decision

**Admin PAT + SSH Deploy Key:**
- Admin tạo Classic PAT (scope `repo`) 1 lần → lưu vào Tab Cấu hình
- Mỗi trạm: GUI tự động tạo repo + sinh SSH key pair + gắn deploy key + generate invite code
- Invite code chứa `ssh_private_key` thay vì PAT
- Deploy key chỉ có quyền trên 1 repo → bảo mật tốt hơn PAT

## Luồng hoạt động

```
┌─────────────────────────────────────────────────────────┐
│  LẦN ĐẦU (1 lần duy nhất)                              │
│                                                         │
│  Admin tạo Classic PAT trên GitHub UI                   │
│  → scope: repo                                          │
│  → Tab "📊 Cấu hình tải dữ liệu" → điền PAT → lưu      │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  MỖI LẦN TẠO TRẠM MỚI (< 1 phút)                      │
│                                                         │
│  Tab "🎫 Tạo mã kích hoạt"                              │
│  Điền: Station ID + Tên trạm + Encryption Key (tuỳ)    │
│  Bấm "🚀 Tạo trạm"                                      │
│                                                         │
│  ① create_repo()        → tạo private repo              │
│  ② generate_ssh_keypair() → Ed25519 key pair (RAM)      │
│  ③ create_deploy_key()  → gắn public key vào repo       │
│  ④ encode_invite_code() → Base64 JSON chứa              │
│     { station_id, station_name, repo_url,               │
│       ssh_private_key, encryption_key }                 │
│  ⑤ Hiển thị mã → Admin copy → gửi trạm                 │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  TRẠM EDGE nhận mã                                      │
│                                                         │
│  Dán invite code → InviteCodeData.auth_type = "ssh"     │
│  → viết SSH key ra temp file → GIT_SSH_COMMAND          │
│  → git clone qua SSH                                    │
│  → lưu key vào Credential Manager → setup PIN           │
└─────────────────────────────────────────────────────────┘
```

## Files đã thay đổi

**Hub:**

| File | Thay đổi |
|------|----------|
| `github_api.py` | `create_deploy_key()`, `generate_ssh_keypair()` (Ed25519) |
| `admin.py` | `encode_invite_code()` thêm param `ssh_private_key`, bỏ `pat` required |
| `gui/tab_invite.py` | Bỏ Device Flow, dùng Admin PAT từ session; tạo repo + deploy key + invite code |

**Edge:**

| File | Thay đổi |
|------|----------|
| `services/invite_code.py` | `InviteCodeData` thêm `ssh_private_key` optional, property `auth_type` |
| `services/git_operations.py` | Hỗ trợ SSH (temp key file + GIT_SSH_COMMAND) + PAT (backward compatible); Windows: `icacls` + LF newline |
| `api/provision_routes.py` | Tự động chọn SSH/PAT theo `auth_type` |

## Backward compatibility

Invite code cũ (có `pat`, không có `ssh_private_key`) → `auth_type = "pat"` → vẫn hoạt động bình thường.

## Cần làm tiếp

- [ ] Test E2E với bot account thật
- [ ] Cập nhật `edge/tests/test_auth_flow.py` cho SSH flow

## Rationale

Deploy key tạo được qua API (khác PAT), chỉ có quyền trên 1 repo cụ thể. Admin chỉ cần 1 PAT để tạo nhiều trạm, mỗi trạm có deploy key riêng biệt.

## Related Documents

- [17. Invite Code Authentication](17_Invite_Code_Authentication.md)
- [29. Hub Operator GUI](29_Hub_Operator_Gui_Streamlit.md)
- [FEATURES/hub_operator_gui.md](../FEATURES/hub_operator_gui.md)
