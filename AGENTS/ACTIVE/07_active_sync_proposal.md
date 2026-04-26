# Active Sync Proposal: Chủ động đóng gói dữ liệu sạch

## Status
**[Proposed - For Sprint 4]**

## Context
Hiện tại, khi có mạng, hệ thống cần đồng bộ dữ liệu khám bệnh về trung tâm (Hub). Nếu chỉ đồng bộ bằng cách dùng Git lưu lịch sử file SQLite hoặc gửi thẳng dữ liệu chưa được làm sạch, sẽ dễ gây xung đột (conflict) ở Hub do dữ liệu rác, nháp hoặc không hoàn thiện.

## Decision
Xây dựng một tính năng "Gửi về Hub" dựa trên nguyên tắc **Chủ động đóng gói dữ liệu sạch**:
1. Cung cấp một nút "Gửi về Hub" trên giao diện Admin/Operator.
2. Khi người dùng bấm nút, hệ thống sẽ **truy vấn và lọc** ra các hồ sơ (Encounters) đã được điền đủ dữ liệu, đạt trạng thái hoàn thành (Clean Data).
3. Đóng gói các dữ liệu này thành một định dạng chuẩn (ví dụ: JSON lines hoặc một file snapshot chuyên biệt).
4. Sử dụng HTTPS/API để gửi gói dữ liệu này đến Hub, thay vì phụ thuộc hoàn toàn vào cơ chế Git sync toàn bộ thư mục `data/`.

## Rationale
- **Tránh Conflict Database**: Git không được sinh ra để merge file nhị phân (SQLite). Gửi từng gói tin JSON rời rạc sẽ dễ dàng hơn nhiều cho Hub khi merge dữ liệu từ hàng trăm trạm.
- **Đảm bảo chất lượng dữ liệu**: Chỉ gửi đi những dữ liệu đã hoàn thiện, giảm tải công sức dọn dẹp tại trung tâm.
- **Tiết kiệm băng thông**: Gửi gói tin JSON nhẹ hơn nhiều so với việc tải lên toàn bộ snapshot của một file SQLite hàng chục MB.
