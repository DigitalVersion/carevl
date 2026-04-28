# Feature: Gateway Authentication (DEPRECATED)

## Trạng thái (Status)
- [ ] Đã triển khai (Deployed)
- [ ] Đang phát triển (In Progress)
- [x] Đã loại bỏ (Deprecated)

**Deprecated Date**: 2026-04-28  
**Replaced By**: [17. Invite Code Authentication](../ACTIVE/17_Invite_Code_Authentication.md)

## Lý do Deprecated

Phương thức Device Flow (5 bước) quá phức tạp cho người dùng cuối và không phù hợp với constraint "không có server backend".

Đã thay thế bằng **Invite Code Authentication** sử dụng Fine-grained PAT:
- Đơn giản hơn: 4 bước thay vì 5 bước
- Không cần GitHub account cá nhân
- Không cần quét QR, nhập device code
- Chỉ cần paste invite code

Xem chi tiết tại: [ARCHIVE/17_GitHub_Device_Flow.md](../ARCHIVE/17_GitHub_Device_Flow.md)

## Mô tả Nghiệp vụ (Business Logic)
Quy trình 5 bước để kích hoạt máy trạm (Gateway) lần đầu:
1. Xác thực thiết bị bằng GitHub Device Flow.
2. Cấu hình URL của Repository đích để lưu trữ dữ liệu.
3. Kiểm tra quyền Ghi (Write) của người dùng; nếu chưa có, sinh mã QR chứa link invite cho Trưởng trạm hoặc Admin Hub quét.
4. Lựa chọn khởi tạo Database trống hoặc Khôi phục Database Snapshot bằng Private Key của Hub.
5. Thiết lập mã PIN 6 số để mã hóa token phục vụ quá trình sử dụng Offline.

## Các Endpoints liên quan (API/UI Routes)
*   `GET /login`: Giao diện hiển thị mã Device Code cho GitHub.
*   `GET/POST /setup/repo`: Nhập và cấu hình Repository đích.
*   `GET/POST /setup/permission`: Hiển thị cảnh báo và mã QR chờ cấp quyền ghi.
*   `GET/POST /setup/data`: Khởi tạo DB trống hoặc Restore DB snapshot.
*   `GET/POST /setup/pin`: Cài đặt mã PIN.

## Lịch sử thay đổi (Changelog)
- **2026-04-27**: Jules - Khởi tạo quy trình Gateway 5 bước và các UI/Endpoint tương ứng.
