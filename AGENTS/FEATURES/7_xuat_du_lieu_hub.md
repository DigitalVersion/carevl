# Feature: 7. Xuat du lieu Hub

## Status
[Active - Implemented]

- UI: xong
- Backend: xong
- Van hanh: chua mo rong

## Context
Tram can day snapshot du lieu len Hub de sao luu, dong bo, va tong hop. He thong phai chay duoc ca luc nguoi dung bam tay, ca luc co Active Sync.

## Decision
Dung man hinh `GET /admin/backups` cho Persona D quan ly snapshot va sync.

- Cho phep sao luu thu cong.
- Hien trang thai dong bo tu dong.
- Nen DB SQLite, ma hoa AES, day len GitHub Releases.
- Theo doi vong doi snapshot de Hub lay ve va giai ma.

## Rationale
Snapshot ma hoa giu an toan du lieu khi roi khoi Edge. GitHub Releases dong vai kho luu trung gian don gian, khong can dung server rieng.

## Related Endpoints
- `GET /admin/backups`

## FHIR/IHE Mapping
- Resources: khong map truc tiep FHIR; tac dong cap DB SQLite va snapshot

## Persona Impact
- Persona D (Truong tram): dung chinh

## Mockup Assets
- `07_hub_sync.png`: man hinh quan ly dong bo va snapshot

## Related Documents
- [Sidebar UI Architecture](sidebar_ui.md)
- [07. Active Sync Protocol: The Encrypted SQLite Blob](../ACTIVE/07_active_sync_protocol.md)
- [15. Hub Aggregation: DuckDB Analytics Pipeline](../ACTIVE/15_Hub_Aggregation.md)
- [18. Two-App Architecture: Edge vs Hub](../ACTIVE/18_Two_App_Architecture.md)
