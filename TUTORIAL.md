# Sổ tay Vận hành CareVL (Visual Tutorial - Windows Edition)

Tài liệu này hướng dẫn chi tiết quy trình cài đặt và sử dụng hệ thống CareVL dành riêng cho môi trường Windows tại các trạm y tế / đoàn khám lưu động.

---

## PHẦN 0: CÀI ĐẶT HỆ THỐNG TRÊN WINDOWS

Hệ thống CareVL được thiết kế để cài đặt "Zero-Config" trên Windows.
**Bước 1:** Nhấn tổ hợp phím `Win + X` trên bàn phím.
**Bước 2:** Chọn "Windows PowerShell (Admin)" hoặc "Terminal (Admin)" từ menu hiện ra.
**Bước 3:** Copy và Paste dòng lệnh cài đặt có trong file `README.md` vào màn hình đen/xanh của PowerShell và nhấn Enter.
**Bước 4:** Chờ đợi script tự động chạy. Sau khi xong, hệ thống sẽ mở trình duyệt và bạn sẽ thấy biểu tượng `CareVL Vĩnh Long` ngoài Desktop để dùng cho những lần sau.

---

## PHẦN 1: KÍCH HOẠT HỆ THỐNG LẦN ĐẦU (THE GATEWAY)

Khi ứng dụng mới được cài đặt, bạn cần thực hiện 5 bước thiết lập ban đầu để sử dụng vĩnh viễn (bao gồm cả khi mất mạng internet).

### Bước 1: Xác thực GitHub (Thiết bị)
Hệ thống sử dụng GitHub để đồng bộ và phân quyền.
1. Dùng điện thoại mở trang `github.com/login/device`.
2. Đăng nhập tài khoản GitHub cá nhân của bạn.
3. Nhập mã code hiển thị trên màn hình máy tính vào điện thoại.
![GitHub Auth](AGENTS/ASSETS/01_github_auth.png)

### Bước 2: Cấu hình Repository
Nhập đường dẫn kho dữ liệu (Repository) mà Hub/Trung tâm đã tạo cho bạn (VD: `DigitalVersion/carevl-data`).
![Repo Config](AGENTS/ASSETS/02_repo_config.png)

### Bước 3: Cấp quyền Ghi (Dành cho Admin)
Nếu tài khoản của bạn chưa được cấp quyền Ghi (Write) vào Repository trên:
1. Màn hình sẽ hiện cảnh báo **Chưa Có Quyền Ghi!**.
2. Đưa **Mã QR** trên màn hình cho Trưởng trạm hoặc Admin Hub quét để mời bạn tham gia nhóm làm việc.
3. Chấp nhận lời mời qua email, sau đó bấm nút "Tôi đã được Admin cấp quyền".
![Permission Gate](AGENTS/ASSETS/03_permission_gate.png)

### Bước 4: Khởi tạo Dữ liệu (Khu vực Cài đặt Nguy hiểm)
Bạn có 2 lựa chọn:
*   **Tạo DB Trống:** Dành cho trạm mới hoàn toàn, chưa từng khám ai.
*   **Khôi phục Snapshot từ Hub:** Dùng khi cài lại máy. Bạn cần xin "Encryption Key" từ Hub để giải mã file dự phòng.
![Data Setup](AGENTS/ASSETS/04_data_setup.png)

### Bước 5: Thiết lập Mã PIN (Đăng nhập Offline)
Tạo 1 mã PIN 6 số. Mã này dùng để mở khóa hệ thống hàng ngày mà không cần mạng Internet. **Tuyệt đối không quên mã PIN này.** Token truy cập sẽ được mã hoá bằng mã PIN của bạn.
![PIN Setup](AGENTS/ASSETS/05_pin_setup.png)

---

## PHẦN 2: THAO TÁC THEO PERSONAS (SAU KHI ĐĂNG NHẬP)

Hệ thống cung cấp một Menu (Sidebar) với 10 chức năng. Thanh menu này sẽ ẩn/hiện tự động trên màn hình điện thoại.

### 1. Persona A: Tiếp nhận
**Vai trò:** Người đứng ở quầy đón bệnh nhân, quét thẻ CCCD và phát mã vạch (Sticker).
**Thao tác:** Chọn mục **1. Tiếp nhận mới** trên Sidebar.
*(Giao diện Sidebar - Mục Tiếp nhận mới)*
![Sidebar - Intake](AGENTS/ASSETS/01_intake_screen.png)

### 2. Persona B: Lâm sàng (Bác sĩ / Điều dưỡng)
**Vai trò:** Khám bệnh trực tiếp, đo sinh hiệu.
Các chức năng liên quan:
*   **2. Lượt khám:** Xem danh sách bệnh nhân đang chờ trước cửa phòng.
*   **3. Hồ sơ bệnh nhân:** Ghi nhận Huyết áp, Nhịp tim, Nhiệt độ trực tiếp vào hồ sơ.

### 3. Persona C: Cập nhật Kết quả (Nhập liệu)
**Vai trò:** Nhân viên phòng Lab cập nhật các xét nghiệm trả chậm.
**Thao tác:** Chọn mục **5. Cập nhật kết quả**.
*(Giao diện Sidebar - Mục Cập nhật kết quả)*
![Sidebar - Results Update](AGENTS/ASSETS/05_results_update.png)

### 4. Persona D: Trưởng Trạm / Quản lý (Admin)
**Vai trò:** Quản lý số liệu, xuất báo cáo và đồng bộ dữ liệu về Hub.
**Thao tác Đồng bộ:** Chọn mục **7. Xuất dữ liệu Hub**.
Quyền tối thượng: Hub Admin là người duy nhất giữ Private Key để giải mã dữ liệu snapshot được gửi lên từ các Edge.
*(Giao diện Admin Backups)*
![Active Sync Complete](AGENTS/ASSETS/07_hub_sync.png)