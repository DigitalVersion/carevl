# Active Sync Protocol: The Encrypted SQLite Blob

## Status
[Active - Sprint 4 Source of Truth]

## Context
CareVL can dua du lieu tu Tram ve Hub an toan va dung goc. Neu sync theo JSON hoac git push thong thuong thi de conflict, de sot du lieu, va kho hop nhat.

## Decision
Dung Encrypted SQLite Blob Protocol qua GitHub Releases.

Quy trinh chuan:
1. Nguoi dung bam `Gui ve Hub` tren UI admin/operator.
2. Tac vu chay ngam qua `fastapi.BackgroundTasks`; UI phai bao ngay `Dang dong goi va gui...`.
3. Ghi `SITE_ID` va timestamp vao metadata ben trong DB.
4. Chay `VACUUM` va `ANALYZE`.
5. Tao snapshot bang API backup de cover WAL, roi ma hoa bang AES-256 voi `ENCRYPTION_KEY`.
6. Dat ten file: `FINAL_{SITE_ID}_YYYY-MM-DDTHH-mm-ss.db.enc`.
7. Upload `.db.enc` len GitHub Releases bang GitHub API voi `GITHUB_TOKEN`.

## Rationale
GitHub Releases dong vai file server cho blob nhi phan, tranh lam phinh git history va tranh conflict merge DB. Metadata ghi ngay trong DB giup Hub xac minh file thuoc tram nao du ten file co bi doi. Chay ngam giu UI khong treo khi upload file lon.

## Related Documents
- [02. SQLite Security & Snapshots](02_SQLite_Security.md)
- [17. Invite Code Authentication: Fine-grained PAT Provisioning](17_Invite_Code_Authentication.md)
- [18. Two-App Architecture: Edge vs Hub](18_Two_App_Architecture.md)
