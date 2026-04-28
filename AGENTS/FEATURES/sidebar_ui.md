# Feature: Responsive Sidebar (FHIR Aligned)

## Status
[Active - Implemented]

- Deployed: co
- In progress: khong
- Deprecated: khong

## Context
He thong co 10 nhom chuc nang. Nguoi dung thuoc 4 persona khac nhau. Can mot thanh dieu huong de tim nhanh dung viec, dung vai tro, dung route, ca tren desktop lan mobile.

## Decision
Dung sidebar responsive lam khung dieu huong chinh.

- Gom 10 muc chuan hoa theo FHIR/IHE.
- Nhom theo 4 persona: Tiep nhan, Lam sang, Nhap lieu, Truong tram.
- Dung Alpine.js cho menu collapse tren mobile.
- Muc chua xong thi tro vao trang coming soon, giu luong dieu huong on dinh.

## Rationale
Mot thanh dieu huong nhat quan giu nguoi dung khong lac. Mobile collapse giu man hinh nho van dung duoc. Sidebar nay cung la ban do route cho toan bo feature ledger.

## Related Endpoints
- `GET /intake`
- `GET /queue`
- `GET /patient-record`
- `GET /aggregate`
- `GET /results-update`
- `GET /reports`
- `GET /admin/backups`
- `GET /audit`
- `GET /settings`
- `GET /about`

## Related Documents
- [1. Tiep nhan moi](1_tiep_nhan_moi.md)
- [2. Luot kham](2_luot_kham.md)
- [3. Ho so benh nhan](3_ho_so_benh_nhan.md)
- [4. Nhap lieu (Aggregate)](4_nhap_lieu_aggregate.md)
- [5. Cap nhat ket qua](5_cap_nhat_ket_qua.md)
- [6. Bao cao](6_bao_cao.md)
- [7. Xuat du lieu Hub](7_xuat_du_lieu_hub.md)
- [8. Lien thong (Audit)](8_lien_thong_audit.md)
- [9. Cai dat tram](9_cai_dat_tram.md)
- [10. Gioi thieu](10_gioi_thieu.md)
