# Feature: 5. Cap nhat ket qua

## Status
[Active]

- UI: xong
- Backend: chua xong
- Van hanh: chua mo

## Context
Ket qua can lam sang den sau kham ban dau. He thong can tim dung phieu, dung nguoi, roi gan ket qua vao dung luot ma khong can tim tay qua nhieu buoc.

## Decision
Dung man hinh `GET /results-update` cho Persona C.

- Quet `Sticker ID` tren phieu chi dinh hoac ket qua.
- Tim dung ca theo ma vach.
- Nhap ket qua xet nghiem, X-Quang, can lam sang.
- Luu du lieu thanh `DiagnosticReport` va `Observation`.

## Rationale
`Sticker ID` la moc noi giua chi dinh va ket qua. Nhan vien nhap lieu khong can tim theo ten hay CCCD, nen nhanh hon va it sai hon.

## Related Endpoints
- `GET /results-update`

## FHIR/IHE Mapping
- Resources: `DiagnosticReport`, `Observation`

## Persona Impact
- Persona C (Nhap lieu): dung chinh

## Mockup Assets
- `05_results_update.png`: man hinh cap nhat ket qua can lam sang

## Related Documents
- [Sidebar UI Architecture](sidebar_ui.md)
- [1. Tiep nhan moi](1_tiep_nhan_moi.md)
- [3. Ho so benh nhan](3_ho_so_benh_nhan.md)
