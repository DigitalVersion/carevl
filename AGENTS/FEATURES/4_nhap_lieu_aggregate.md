# Feature: 4. Nhap lieu (Aggregate)

## Status
[Planned]

- UI: chua xong
- Backend: chua xong
- Van hanh: chua mo

## Context
Co nhieu so lieu tong hop khong gan tung benh nhan. Tram van can nhap de bao cao dung mau, dung ky, dung tong.

## Decision
Dung man hinh `GET /aggregate` cho Persona C nhap so lieu tong hop.

- Form theo mau bao cao.
- Khong rang buoc vao `Patient` hay `Encounter` cu the.
- Luu du lieu duoi dang `MeasureReport`.

## Rationale
Tach nhap lieu tong hop khoi ho so ca nhan giup mo hinh sach hon. Bao cao tong hop di mot nhanh rieng, khong lam ban ho so lam sang.

## Related Endpoints
- `GET /aggregate`

## FHIR/IHE Mapping
- Resources: `MeasureReport`

## Persona Impact
- Persona C (Nhap lieu): dung chinh

## Mockup Assets
- `04_aggregate_entry.png`: form nhap so lieu tong hop

## Related Documents
- [Sidebar UI Architecture](sidebar_ui.md)
- [6. Bao cao](6_bao_cao.md)
- [15. Hub Aggregation: DuckDB Analytics Pipeline](../ACTIVE/15_Hub_Aggregation.md)
