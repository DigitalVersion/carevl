# Feature: 3. Ho so benh nhan

## Status
[Planned]

- UI: chua xong
- Backend: chua xong
- Van hanh: chua mo

## Context
Bac si can mot noi xem thong tin benh nhan, ghi sinh hieu, va doc lich su. Khong co man nay thi kham xong roi du lieu van roi rac.

## Decision
Dung man hinh `GET /patient-record` lam ho so thao tac chinh cho Persona B.

- Hien thong tin `Patient`.
- Ghi sinh hieu: huyet ap, nhip tim, nhiet do.
- Doc lich su lien quan va tinh trang da biet.
- Luu du lieu thanh `Observation` va `Condition` khi can.

## Rationale
Ho so tap trung giup bac si xem va ghi trong mot luong. Du lieu song duoc chuan hoa tu dau, de bao cao va dong bo ve sau de hon.

## Related Endpoints
- `GET /patient-record`

## FHIR/IHE Mapping
- Resources: `Observation`, `Patient`, `Condition`

## Persona Impact
- Persona B (Lam sang): dung chinh

## Mockup Assets
- `03_patient_record.png`: man hinh chi tiet ho so va nhap sinh hieu

## Related Documents
- [Sidebar UI Architecture](sidebar_ui.md)
- [2. Luot kham](2_luot_kham.md)
- [5. Cap nhat ket qua](5_cap_nhat_ket_qua.md)
