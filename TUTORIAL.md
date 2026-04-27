# Sổ tay Vận hành CareVL (Visual Tutorial)

Tài liệu này hướng dẫn sử dụng ứng dụng CareVL dựa trên 4 vai trò (Personas) chính trong trạm y tế / đoàn khám.

---

## Bảng điều khiển (Sidebar)

Hệ thống cung cấp một Menu (Sidebar) với 10 chức năng, được thiết kế theo chuẩn FHIR. Thanh menu này sẽ ẩn/hiện tự động trên màn hình điện thoại.

| Nhóm | # | Mục Sidebar | Vai trò (Persona) |
|---|---|---|---|
| **TIẾP NHẬN** | 1 | **Tiếp nhận mới** | Lễ tân / Người phát số (Persona A) |
| **LÂM SÀNG** | 2 | **Lượt khám** | Bác sĩ / Điều dưỡng (Persona B) |
|  | 3 | **Hồ sơ bệnh nhân** | Bác sĩ / Điều dưỡng (Persona B) |
| **NHẬP LIỆU** | 4 | **Nhập liệu (Aggregate)** | Người trực trạm (Persona C) |
|  | 5 | **Cập nhật kết quả** | Người cập nhật xét nghiệm (Persona C) |
| **QUẢN TRỊ** | 6 | **Báo cáo** | Trưởng trạm (Persona D) |
|  | 7 | **Xuất dữ liệu Hub** | Trưởng trạm / Admin (Persona D) |
| **HỆ THỐNG** | 8 | **Liên thông (Audit)** | IT / Hỗ trợ kỹ thuật |
|  | 9 | **Cài đặt trạm** | Trưởng trạm |
|  | 10 | **Giới thiệu** | Mọi người |

---

## 1. Persona A: Tiếp nhận

**Vai trò:** Người đứng ở quầy đón bệnh nhân, quét thẻ CCCD và phát mã vạch (Sticker).

**Thao tác:**
1. Chọn mục **1. Tiếp nhận mới** trên Sidebar.
2. Quét hoặc nhập số CCCD của bệnh nhân.
3. Quét mã vạch trên tờ tem nhãn (Sticker ID).
4. Bấm "Phát tem & Xếp hàng".

*(Giao diện Sidebar - Mục Tiếp nhận mới)*
![Sidebar - Intake](AGENTS/ASSETS/sidebar_desktop.png)

---

## 2. Persona B: Lâm sàng (Bác sĩ / Điều dưỡng)

**Vai trò:** Khám bệnh trực tiếp, đo sinh hiệu.

*(Tính năng hiện đang trong quá trình phát triển - Coming Soon)*
![Coming Soon](AGENTS/ASSETS/sidebar_placeholder.png)

Các chức năng sắp ra mắt:
*   **2. Lượt khám:** Xem danh sách bệnh nhân đang chờ trước cửa phòng.
*   **3. Hồ sơ bệnh nhân:** Ghi nhận Huyết áp, Nhịp tim, Nhiệt độ trực tiếp vào hồ sơ.

---

## 3. Persona C: Cập nhật Kết quả (Nhập liệu)

**Vai trò:** Nhân viên phòng Lab hoặc người trực cập nhật các xét nghiệm trả chậm (Cận lâm sàng, X-Quang).

**Thao tác:**
1. Mở điện thoại, chọn mục **5. Cập nhật kết quả**.
2. Dùng camera điện thoại quét mã vạch trên phiếu kết quả (Sticker ID).
3. Nhập các chỉ số bổ sung.
4. Bấm Lưu.

*(Giao diện Sidebar - Mục Cập nhật kết quả)*
![Sidebar - Results Update](AGENTS/ASSETS/sidebar_active_state.png)

---

## 4. Persona D: Trưởng Trạm / Quản lý (Admin)

**Vai trò:** Quản lý số liệu, xuất báo cáo và đồng bộ dữ liệu về Trung tâm (Hub).

**Thao tác Đồng bộ:**
1. Chọn mục **7. Xuất dữ liệu Hub**.
2. Hệ thống sẽ tự động sao lưu dữ liệu mỗi 15 phút.
3. Bạn có thể bấm "Tạo Snapshot Ngay" để sao lưu tức thì.
4. Bấm "Gửi dữ liệu về Hub" để tải gói dữ liệu bảo mật lên hệ thống trung tâm.

*(Giao diện Admin Backups - Active Sync)*
![Active Sync Complete](AGENTS/ASSETS/sync_complete.png)