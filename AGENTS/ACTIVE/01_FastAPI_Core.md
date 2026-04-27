# FastAPI Core Architecture

## Status
**[Active]**

## Context
Dự án CareVL ban đầu được xây dựng trên nền tảng CustomTkinter cho ứng dụng Desktop. Tuy nhiên, kiến trúc này gây khó khăn trong việc phát triển giao diện responsive cho thiết bị di động (Contributor dùng điện thoại để quét mã vạch) và hạn chế khả năng mở rộng API.

## Decision
Chuyển đổi toàn bộ kiến trúc Backend sang sử dụng FastAPI.

## Rationale
- **Tốc độ & Hiện đại**: FastAPI cung cấp hiệu năng rất cao, hỗ trợ Async/Await tự nhiên và Pydantic cho validation.
- **Tách biệt Frontend/Backend**: FastAPI cho phép phục vụ API và trả về HTML template (Jinja2) một cách độc lập, giúp dễ dàng tích hợp TailwindCSS và HTMX.
- **Dễ bảo trì**: Cấu trúc thư mục dạng module (core, api, models, services) rõ ràng hơn kiến trúc monolithic cũ. Lỗi sẽ dễ khoanh vùng hơn.
- **Web-based UI**: Cho phép Contributor sử dụng điện thoại để quét mã vạch và nhập dữ liệu.

## Platform Support
**Hệ thống chỉ hỗ trợ Windows 10/11.** Không hỗ trợ macOS hoặc Linux.

Lý do:
- Các trạm y tế tại Vĩnh Long sử dụng Windows
- Script cài đặt và automation được tối ưu cho PowerShell
- Một số dependency và workflow được thiết kế đặc thù cho Windows
- Đơn giản hóa testing và deployment cho một platform duy nhất
