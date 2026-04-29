# Invite Code Authentication: Fine-grained PAT Provisioning

## Status
[Active - Implemented]

Test Status: ✅ Fully tested (17/17 tests passing)
- Unit tests: `edge/tests/test_auth_flow.py`
- Manual demo: `edge/tests/manual_auth_test.py`
- Test documentation: `edge/tests/README.md`

## Context
CareVL can cach xac thuc don gian cho tram:
- khong can backend server
- khong doi ky nang Git/GitHub/OAuth
- chi dua vao GitHub
- setup trong khoang 5 phut

Rang buoc:
- khong co ngan sach infrastructure
- nguoi dung cuoi khong biet Git
- van phai du an toan cho du lieu y te cong dong

## Decision
Dung GitHub Fine-grained PAT voi Invite Code provisioning.

### Mo hinh cot loi
- `1 repo = 1 may tram`, khong phai `1 user`
- Doi may thi dung lai invite code cu, chon `Restore`, pull du lieu ve
- Khong gan voi GitHub account ca nhan

Vi du:
- `station-001` repo -> may so 1 tai mot tram
- May hong -> cai may moi -> nhap lai invite code -> restore du lieu

### Snapshot luu dau
- Dung GitHub Releases
- File ten: `FINAL_{SITE_ID}_YYYY-MM-DDTHH-mm-ss.db.enc`
- PAT phai co `Contents: write`
- Khong commit SQLite vao code repo

### Hub workflow
1. Dung script Python list releases tu nhieu repo
2. Download `.db.enc`
3. Giai ma bang `ENCRYPTION_KEY`
4. Aggregate bang DuckDB, co the query truc tiep SQLite qua `sqlite_scan(...)`
5. Tao bao cao tong hop

### Kien truc setup
```text
Hub Admin mot lan:
1. Tao bot account
2. Tao nhieu repo
3. Tao nhieu PAT fine-grained
4. Xuat invite code
5. Gui code qua Zalo/Email

Tram:
1. Nhap invite code
2. App parse code
3. Luu PAT vao Credential Manager
4. Git clone/pull voi PAT
5. Setup PIN
6. Ready
```

### Technical implementation
Hub Admin:
1. Tao bot GitHub account
2. Tao repo bang script nhu `scripts/hub_setup_repos.py`
3. Tao fine-grained PAT thu cong qua GitHub UI
4. Luu PAT vao CSV
5. Sinh invite code bang Base64 JSON tu `station_id`, `station_name`, `repo_url`, `pat`

Tram:
1. UI nhap invite code
2. Backend decode Base64, parse JSON, validate key bat buoc
3. Luu PAT vao Windows Credential Manager qua `keyring`
4. Clone/push git voi PAT

Chi tiet quan trong:
- Fine-grained PAT khong tao qua API; phai tao thu cong
- `Contents: write` bao gom git operations va release asset upload
- PAT luu secure trong Windows Credential Manager
- Git URL co the inject PAT de clone; push dung credential helper/env bien

### Security analysis
Threat chinh va giam thieu:
- PAT lo qua Zalo/Email -> chi lo `1` repo; co the revoke ngay
- PAT bi lay tu may tram -> gioi han anh huong `1` tram; luu trong Credential Manager
- Bot account bi compromise -> bat `2FA`, chi Hub Admin giu, theo doi audit log
- Man-in-the-middle -> git dung HTTPS/TLS

Trade-off chap nhan:
- PAT lo co the lam lo du lieu `1` tram
- Tao PAT thu cong rat ton tay luc dau
- Audit chi tiet khong dep nhu he thong co server

### Tai sao khong dung cach khac
- Khong GitHub App: can server va callback OAuth
- Khong Device Flow: phuc tap, doi GitHub account, token expire va can refresh
- Chon fine-grained PAT: scope theo repo, khong can server, khong expire neu dat `No expiration`, UX don gian

### Checklist
Hub Admin:
- [x] Tao bot account co `2FA`
- [x] Tao private repo
- [x] Tao PAT fine-grained
- [x] Export invite code
- [x] Gui code cho tram

Station App:
- [x] Co UI nhap invite code
- [x] Parse/validate code
- [x] Luu PAT vao Credential Manager
- [x] Clone/pull/push bang PAT
- [x] Ho tro `New DB` va `Restore DB`
- [x] Setup PIN

Testing:
- [x] Test parse invite code (6 tests)
- [x] Test luu/lay PAT (3 tests)
- [x] Test clone/push (4 tests)
- [x] Test revoke PAT (covered in credential tests)
- [x] Test PAT sai/het han (covered in validation tests)
- [x] Test PIN encryption (2 tests)
- [x] Test end-to-end flow (2 tests)
- [x] **Total: 17/17 tests passing ✅**

Migration:
- Device Flow da dua vao archive
- Ly do doi: PAT don gian hon, it buoc hon, khong doi account ca nhan, hop rang buoc khong co server

## Rationale
Fine-grained PAT la cach re, de, va vua du an toan trong bai toan nay. Moi tram chi giu quyen tren repo cua no. Hub van tong hop duoc qua snapshot va DuckDB ma khong can backend rieng.

## Related Documents
- [02. SQLite Security & Snapshots](02_SQLite_Security.md)
- [07. Active Sync Protocol: The Encrypted SQLite Blob](07_active_sync_protocol.md)
- [14. Bootstrap Infrastructure: One-Liner Setup](14_Bootstrap_Infrastructure.md)
- [18. Two-App Architecture: Edge vs Hub](18_Two_App_Architecture.md)
- [23. Authentication Testing Guide](23_Auth_Testing_Guide.md)
- [../ARCHIVE/17_GitHub_Device_Flow.md](../ARCHIVE/17_GitHub_Device_Flow.md)
