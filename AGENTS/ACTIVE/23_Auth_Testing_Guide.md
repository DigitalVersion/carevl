# Authentication Testing Guide

## Status
[Active - Implemented]

## Context
Hệ thống Invite Code Authentication cần test đầy đủ để đảm bảo an toàn và hoạt động đúng. Document này mô tả test suite và cách chạy test.

## Test Files

### `edge/tests/test_auth_flow.py` - Automated Unit Tests

Comprehensive pytest suite covering all authentication components:

**Test Coverage:**
- ✅ Invite code encoding/decoding
- ✅ Invite code validation (valid/invalid cases)
- ✅ Credential Manager (PAT and encryption key storage)
- ✅ Git operations (clone, pull, push)
- ✅ PIN-based encryption/decryption
- ✅ End-to-end new station setup flow
- ✅ End-to-end restore station flow

**Run Tests:**
```bash
# Run all tests
uv run pytest edge/tests/test_auth_flow.py -v

# Run specific test class
uv run pytest edge/tests/test_auth_flow.py::TestInviteCodeValidation -v

# Run with coverage
uv run pytest edge/tests/test_auth_flow.py --cov=app.services --cov-report=html
```

**Test Results:**
```
17 tests passed ✅
- 6 invite code tests
- 3 credential manager tests
- 4 git operations tests
- 2 PIN encryption tests
- 2 end-to-end flow tests
```



## Authentication Flow Overview

### Hub Admin Workflow

1. **Create Bot Account**
   - Create GitHub bot account with 2FA
   - Create private repositories (1 per station)

2. **Generate Fine-grained PAT**
   - Manually create PAT via GitHub UI
   - Scope: `Contents: write` for specific repo
   - Expiration: `No expiration` (or long-lived)

3. **Generate Invite Code**
   ```python
   from app.services.invite_code import InviteCodeService
   
   data = {
       "station_id": "TRAM_001",
       "station_name": "Trạm Y Tế Xã A",
       "repo_url": "https://github.com/bot/station-001",
       "pat": "ghp_xxxxxxxxxxxx",
       "encryption_key": "optional-32-byte-key"
   }
   
   invite_code = InviteCodeService.encode(data)
   # Send via Zalo/Email to station
   ```

4. **Send to Stations**
   - Send invite code via Zalo or Email
   - One code per station
   - Code contains everything needed for setup

### Station Workflow

1. **Enter Invite Code**
   - Open provisioning UI (`/provision`)
   - Paste invite code
   - Click "Validate"

2. **Choose Setup Mode**
   - **New Station**: Initialize empty database
   - **Restore**: Download latest snapshot from GitHub Releases

3. **Automatic Setup**
   - App validates invite code
   - Saves PAT to Windows Credential Manager
   - Clones repository using PAT
   - Initializes or restores database

4. **Set PIN**
   - Enter 6-digit PIN
   - PIN encrypts GitHub token for offline access
   - PIN required for subsequent logins

5. **Ready to Use**
   - Redirect to dashboard
   - Start recording patient data
   - Automatic sync to GitHub

## Security Features

### Credential Storage
- **Windows Credential Manager**: PAT stored securely in OS keyring
- **No plaintext storage**: Never stored in files or environment variables
- **Per-station isolation**: Each station has separate credentials

### PIN Protection
- **PBKDF2 encryption**: 480,000 iterations with SHA-256
- **Random salt**: Unique salt per installation
- **Offline access**: Decrypt token using PIN when offline
- **Brute-force resistant**: High iteration count prevents attacks

### Git Operations
- **HTTPS with PAT**: Secure authentication over TLS
- **Fine-grained scope**: PAT limited to single repository
- **Revocable**: Hub admin can revoke PAT anytime
- **Audit trail**: GitHub tracks all operations

### Threat Mitigation

| Threat | Mitigation |
|--------|-----------|
| PAT leaked via Zalo/Email | Only affects 1 station; revoke immediately |
| PAT stolen from station PC | Stored in Credential Manager; limited scope |
| Bot account compromised | 2FA required; audit logs; revoke all PATs |
| Man-in-the-middle | Git uses HTTPS/TLS |
| Wrong PIN attempts | Cryptographic failure; no retry limit needed |

## Testing Checklist

### Before Deployment

- [ ] All unit tests pass (`pytest`)
- [ ] Manual test completes successfully
- [ ] Git is installed on target machines
- [ ] Windows Credential Manager is accessible
- [ ] GitHub bot account created with 2FA
- [ ] Test repositories created
- [ ] Test PATs generated and validated
- [ ] Invite codes generated and tested
- [ ] PIN setup and verification works
- [ ] Database initialization works
- [ ] Database restore works (if applicable)

### After Deployment

- [ ] Station can enter invite code
- [ ] Credentials saved successfully
- [ ] Repository cloned successfully
- [ ] PIN login works offline
- [ ] Data syncs to GitHub
- [ ] Snapshots uploaded to Releases
- [ ] Hub can aggregate data from multiple stations

## Troubleshooting

### Common Issues

**Issue: "Git not found"**
- Solution: Install Git from https://git-scm.com/download/win
- Verify: Run `git --version` in terminal

**Issue: "Failed to save PAT"**
- Solution: Check Windows Credential Manager is accessible
- Verify: Open Control Panel → Credential Manager

**Issue: "Invalid invite code"**
- Solution: Check code wasn't truncated when copying
- Verify: Code should be valid Base64 (no special chars)

**Issue: "Repository clone failed"**
- Solution: Check PAT has `Contents: write` permission
- Verify: Try cloning manually with PAT

**Issue: "Wrong PIN"**
- Solution: Re-enter correct 6-digit PIN
- Note: No recovery mechanism; must re-provision if forgotten

## Rationale
Test coverage đầy đủ đảm bảo authentication flow hoạt động đúng trước khi deploy. Mock external dependencies (Git, keyring) để test nhanh và không phụ thuộc môi trường.

## Related Documents
- [17. Invite Code Authentication](17_Invite_Code_Authentication.md)
- [Auth Gateway Feature (Deprecated)](../FEATURES/auth_gateway.md)
- [18. Two-App Architecture](18_Two_App_Architecture.md)
- [02. SQLite Security & Snapshots](02_SQLite_Security.md)
