# Feature: 8. Lien thong (Audit)

## Status
[Planned]

- UI: chua xong
- Backend: chua xong
- Van hanh: chua mo

## Context
Du lieu y te can truy vet thay doi va goc ket noi ben ngoai. Neu co su co, truong tram phai lan ra ai sua, sua luc nao, du lieu di dau.

## Decision
Dung man hinh `GET /audit` cho Persona D xem audit va quan ly lien thong.

- Hien lich su thay doi du lieu.
- Ghi nhan cac su kien lien thong voi he thong ngoai.
- Doc va loc `AuditEvent` theo thoi gian, nguoi dung, doi tuong.

## Rationale
Audit ro rang giup van hanh an tam hon, de doi chieu hon, va dung huong voi yeu cau truy vet trong he thong y te.

## Related Endpoints
- `GET /audit`

## FHIR/IHE Mapping
- Resources: `AuditEvent`

## Persona Impact
- Persona D (Truong tram): dung chinh

## Mockup Assets
- `08_audit_logs.png`: man hinh lich su thay doi he thong

## Related Documents
- [Sidebar UI Architecture](sidebar_ui.md)
- [07. Active Sync Protocol: The Encrypted SQLite Blob](../ACTIVE/07_active_sync_protocol.md)
- [10. Quy che van hanh](../ACTIVE/10_Quy_Che_Van_Hanh.md)
