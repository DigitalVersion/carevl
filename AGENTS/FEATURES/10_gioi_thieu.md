# Feature: 10. Gioi thieu

## Status
[Planned]

- UI: chua xong
- Backend: chua xong
- Van hanh: chua mo

## Context
Nguoi dung can biet ban dang chay ban nao, xem huong dan nhanh, va tim kenh ho tro khi co van de. Khong co trang nay thi luc gap loi, moi nguoi hoi nhau bang mieng.

## Decision
Dung man hinh `GET /about` de hien thong tin he thong.

- Hien version phan mem.
- Hien huong dan dung nhanh.
- Hien thong tin nhom phat trien va ho tro.

## Rationale
Mot trang thong tin nho nhung giai ap luc ho tro. Nguoi dung tu soi ban, tu tim link, tu biet goi ai.

## Related Endpoints
- `GET /about`

## FHIR/IHE Mapping
- Resources: khong co

## Persona Impact
- Tat ca persona: deu xem duoc

## Mockup Assets
- `10_about.png`: man hinh thong tin he thong va nhom phat trien

## Related Documents
- [Sidebar UI Architecture](sidebar_ui.md)
- [08. Huong dan Admin](../ACTIVE/08_Huong_Dan_Admin.md)
