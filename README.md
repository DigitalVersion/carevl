# CareVL (Care Vĩnh Long)

Hệ thống Hồ sơ Sức khỏe Điện tử (EHR) offline-first được thiết kế đặc biệt cho các trạm y tế và đoàn khám lưu động tại Vĩnh Long. Hệ thống hoạt động mượt mà ngay cả khi không có Internet và tự động đồng bộ dữ liệu an toàn về máy chủ trung tâm khi có mạng.

---

## 🚀 Cài đặt (1 dòng lệnh)

Hệ thống tự động cài đặt mọi thứ cần thiết. Không cần cài đặt gì thêm!

**Cách cài:** Mở **PowerShell** với quyền **Run as Administrator** (nhấn `Win + X` → chọn Terminal/PowerShell Admin), sau đó dán 1 trong 2 lệnh:

### Bản Chính thức (Stable - Khuyên dùng)
```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; iwr -useb https://raw.githubusercontent.com/DigitalVersion/carevl/main/scripts/setup.ps1 | iex
```

### Bản Thử nghiệm (Canary)
```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; iwr -useb https://raw.githubusercontent.com/DigitalVersion/carevl/canary/scripts/setup.ps1 | iex
```

---

## 📖 Hướng dẫn sử dụng

Xem hướng dẫn chi tiết với hình ảnh tại: **[TUTORIAL.md](TUTORIAL.md)**

---

## 🎯 Tổng quan hệ thống

### Vấn đề
- Tỉnh Vĩnh Long có ~100 trạm y tế xã/phường
- Mỗi năm khám sức khỏe định kỳ cho hàng trăm ngàn người dân
- Nhân viên y tế làm việc ngoài thực địa, thường xuyên offline
- Hub cần tổng hợp dữ liệu từ các trạm

### Giải pháp CareVL
- **Offline-first**: Hoạt động hoàn toàn không cần mạng
- **Active Sync**: Đồng bộ dữ liệu mã hóa an toàn qua GitHub
- **Web-based**: Giao diện responsive cho Desktop và Mobile
- **4 vai trò**: Operator, Contributor, Reviewer, Admin
- **Tuân thủ chuẩn**: FHIR/IHE (chuẩn y tế quốc tế)

---

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python 3.11+) với Async/Await
- **Database**: SQLite với WAL mode (Write-Ahead Logging)
- **Bảo mật**: AES-256 encryption, GitHub OAuth + PIN 6 số offline
- **Frontend**: Jinja2 Templates + Tailwind CSS + Alpine.js + HTMX
- **Package Manager**: `uv` (nhanh hơn pip/poetry)
- **Offline-Ready**: 100% Local assets (không dùng CDN)

**Lưu ý**: Hệ thống chỉ hỗ trợ Windows 10/11

---

## 🗄️ Cấu trúc thư mục

```text
carevl/
├── app/                    # Mã nguồn FastAPI
│   ├── main.py            # Entry point
│   ├── core/              # Config, Database, Identity
│   ├── api/               # Routes (auth, admin, ui, endpoints)
│   ├── models/            # SQLAlchemy Models
│   ├── services/          # Business Logic (crypto, sync, snapshot)
│   ├── templates/         # Jinja2 HTML Templates
│   └── static/            # CSS, JS, Assets
│
├── config/                # Cấu hình hệ thống
├── data/                  # SQLite Database + Backups
└── legacy/                # Code cũ (Đã Archive)
```

---

## 🚦 Cách hoạt động

```
[Trạm 1]  → Nhập liệu offline → Đồng bộ khi có mạng
[Trạm 2]  → Nhập liệu offline → Đồng bộ khi có mạng
[Trạm 3]  → Nhập liệu offline → Đồng bộ khi có mạng
                    ↓
          [Hub] → Tổng hợp → Báo cáo
```

### Quy tắc vận hành

- Mỗi trạm chỉ dùng trên **một máy chính thức**
- Khi có mạng, dùng nút **"Gửi về Hub"** trong app
- Nếu cần sao lưu, dùng chức năng **"Xuất dữ liệu"**
- Nếu có sự cố, dừng lại và báo Hub/Admin ngay

---

## 💬 Hỗ trợ

Mọi thắc mắc vui lòng liên hệ Bộ phận IT của Trung tâm Y tế hoặc tạo Issue tại GitHub.

**Yêu cầu hệ thống**: Windows 10/11

---

## 👨‍💻 Tác giả

**Nguyễn Minh Phát**, MSc Medical Sciences  
GitHub: [@kanazawahere](https://github.com/kanazawahere)  
Email: kanazawahere@gmail.com

---

## 📚 Tài liệu kỹ thuật

Dành cho Developer và AI Agent:
- **[AGENTS.md](AGENTS.md)**: Kiến trúc hệ thống, ADR, Memory Vault
- **[TUTORIAL.md](TUTORIAL.md)**: Hướng dẫn sử dụng chi tiết

---

**Built with ❤️ for Vĩnh Long healthcare workers**
