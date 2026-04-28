# Feature: 2. Luot kham

## Status
[Planned]

- UI: chua xong
- Backend: chua xong
- Van hanh: chua mo

## Context
Bac si can thay hang cho sau tiep nhan, chon dung benh nhan, mo dung ca kham. Neu khong co lop nay, dong kham bi dut doan.

## Decision
Dung man hinh `GET /queue` lam diem vao cho Persona B.

- Lay danh sach `Encounter` dang cho kham.
- Cho bac si chon benh nhan de bat dau ca.
- Khi bat dau, `Encounter` chuyen sang `in-progress`.

## Rationale
Hang cho rieng giup bac si thay thu tu ro, giam mo nham ho so, giam tac vu trao doi bang tay giua quay va phong kham.

## Related Endpoints
- `GET /queue`

## FHIR/IHE Mapping
- Resources: `Encounter`
- Mapping: luot duoc mo o trang thai `in-progress` khi bac si nhan ca

## Persona Impact
- Persona B (Lam sang): dung chinh

## Mockup Assets
- `02_queue_screen.png`: man hinh hang cho bac si

## Related Documents
- [Sidebar UI Architecture](sidebar_ui.md)
- [1. Tiep nhan moi](1_tiep_nhan_moi.md)
- [3. Ho so benh nhan](3_ho_so_benh_nhan.md)
