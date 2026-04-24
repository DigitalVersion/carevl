# Admin

Thư mục này dành cho Hub/Admin và tester kiểm thử luồng quản trị.

## Nguyên tắc

- Đây là khu vực của `admin tools`
- Không dùng để nhập liệu hằng ngày như tại trạm
- Đây là nơi xử lý danh sách trạm, cấu hình, checklist và aggregate dữ liệu

## Phạm vi kiểm thử

Trong thư mục này, có thể test:

- kiểm tra danh sách trạm
- tạo `stations.json` từ CSV
- xuất onboarding checklist
- gom aggregate dữ liệu toàn hệ thống
- đọc tài liệu vận hành và nghiệp vụ admin

Không test tại đây:

- CRUD hồ sơ hằng ngày của trạm
- luồng người dùng thông thường

## Các file thường dùng

- `Launch-Admin-App.bat`
- `Check-Stations.bat`
- `Build-Stations-Json.bat`
- `Export-Onboarding-Checklist.bat`
- `Aggregate-System-Data.bat`

## Tài liệu liên quan

- `../HUONG_DAN_ADMIN.md`
- `../QUY_CHE_VAN_HANH.md`

## Gợi ý cho tester

- Nếu đang test nghiệp vụ của trạm, chuyển sang `Onboarding/`
- Nếu đang test nghiệp vụ quản trị, ở lại `Admin/`
