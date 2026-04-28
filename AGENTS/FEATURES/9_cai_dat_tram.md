# Feature: 9. Cai dat tram

## Status
[Planned]

- UI: chua xong
- Backend: chua xong
- Van hanh: chua mo

## Context
Moi tram can tu giu cau hinh co so, PIN, va bien moi truong can thiet. Neu phai sua file thu cong, nguy co sai cao va kho ban giao.

## Decision
Dung man hinh `GET /settings` cho Persona D quan ly cau hinh tram.

- Sua thong tin co so kham.
- Doi ma PIN bao ve.
- Cap nhat gia tri `.env` tu UI co kiem soat.

## Rationale
Dua cau hinh thong dung vao UI giup giam can shell, giam loi thao tac, de huan luyen va van hanh tai diem.

## Related Endpoints
- `GET /settings`

## FHIR/IHE Mapping
- Resources: khong co; pham vi system level

## Persona Impact
- Persona D (Truong tram): dung chinh

## Mockup Assets
- `09_station_settings.png`: man hinh cau hinh he thong tram

## Related Documents
- [Sidebar UI Architecture](sidebar_ui.md)
- [08. Huong dan Admin](../ACTIVE/08_Huong_Dan_Admin.md)
- [14. Bootstrap Infrastructure: One-Liner Setup](../ACTIVE/14_Bootstrap_Infrastructure.md)
