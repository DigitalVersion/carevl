# CareVL (Care Vĩnh Long) - Edge Edition

CareVL là hệ thống Hồ sơ Sức khỏe Điện tử (EHR) được tối ưu hóa đặc biệt cho các trạm y tế và đoàn khám lưu động, với khả năng hoạt động offline (không cần internet) và tự động đồng bộ hóa dữ liệu (Active Sync).

## Luồng nghiệp vụ tổng quan (end-to-end)

Sơ đồ dưới mô tả chuỗi từ cấp phép Hub → trạm → vận hành → snapshot → Hub → báo cáo / liên thông (chi tiết số bước trong tài liệu nội bộ).

![CareVL — luồng nghiệp vụ end-to-end](AGENTS/ASSETS/overview_end_to_end.svg)

*Tài liệu kèm sơ đồ, Mermaid và bảng: [26. Visualization Catalog](AGENTS/ACTIVE/26_Visualization.md). Phạm vi thu thập dữ liệu (nghiệp vụ): [27. Phạm vi thu thập dữ liệu nghiệp vụ](AGENTS/ACTIVE/27_Business_Data_Intake_Scope.md).*

---

## Cài đặt Windows — một lệnh (chọn nhánh `main` hoặc `canary`)

Cùng một script cài đặt; chỉ **khác URL** theo nhánh Git bạn muốn dùng:

| Nhánh | Khi nào dùng |
|-------|----------------|
| **`main`** | Bản **ổn định**, khuyên dùng cho vận hành hàng ngày tại trạm. |
| **`canary`** | Bản **thử nghiệm** — tính năng Gateway, xác thực và bảo mật offline (PIN) mới hơn; có thể thay đổi nhanh. |

**Yêu cầu:** mở **PowerShell** bằng quyền **Quản trị viên** (*Run as Administrator*), rồi dán **một** trong hai lệnh sau.

**Ổn định (`main`):**

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; iwr -useb https://raw.githubusercontent.com/DigitalVersion/carevl/main/scripts/setup.ps1 | iex
```

**Thử nghiệm (`canary`):**

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; iwr -useb https://raw.githubusercontent.com/DigitalVersion/carevl/canary/scripts/setup.ps1 | iex
```

---

## Hỗ trợ

Mọi thắc mắc trong quá trình cài đặt hoặc vận hành, vui lòng liên hệ Bộ phận IT của Trung tâm Y tế.

*Lưu ý: Hệ thống được thiết kế ưu tiên cho hệ điều hành Windows tại các cơ sở khám chữa bệnh.*
