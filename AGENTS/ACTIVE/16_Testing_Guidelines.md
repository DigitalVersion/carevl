# Testing Guidelines

## Status
[Active]

## Context
Script cai dat can test duoc ca truong hop may moi lan dau, ca truong hop update code ma khong mat du lieu.

## Decision
Dung `test_fresh_install.ps1` de test fresh install nhieu lan tren cung may. Dung `setup.ps1` de test update.

### Test fresh install
Chay:
```powershell
.\scripts\test_fresh_install.ps1
.\scripts\test_fresh_install.ps1 -Branch main
```

Script se:
1. Xoa `$HOME\carevl-app` neu co
2. Xoa shortcut `CareVL Vinh Long` tren Desktop neu co
3. Tai va chay `setup.ps1` tu GitHub
4. Gia lap may moi hoan toan

Canh bao:
- Script nay xoa toan bo du lieu trong `carevl-app`
- Chi dung de test
- Khong dung tren production
- Nen chay PowerShell voi quyen Administrator

### Test update
Chay:
```powershell
.\scripts\setup.ps1
```

Script se:
- Backup `.env` va `data/`
- Pull code moi
- Restore `.env` va `data/`

So sanh:
- Fresh install: `test_fresh_install.ps1`, co xoa du lieu, dung de gia lap may moi
- Update: `setup.ps1`, khong xoa du lieu, dung de test idempotent update
- Production: `setup.ps1`, khong xoa du lieu

## Rationale
Tach fresh install khoi update giup khong nham test pha du lieu voi test cap nhat. Day la cach nhanh de kiem tra script cai dat co that su lap lai duoc hay khong.

## Related Documents
- [14. Bootstrap Infrastructure: One-Liner Setup](14_Bootstrap_Infrastructure.md)
- [04. Development Guidelines & Troubleshooting](04_Development_Guidelines.md)
