# Bootstrap Infrastructure: One-Liner Setup

## Status
**[Active]**

## Context
Các trạm y tế cần cài đặt hệ thống nhanh chóng mà không cần kiến thức kỹ thuật. Cần có script tự động cài đặt mọi thứ cần thiết chỉ với 1 dòng lệnh.

## Decision
Xây dựng script `setup.ps1` với khả năng "tự sinh tự dưỡng" (self-bootstrapping).

## Implementation

### One-Liner Command
```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; iwr -useb https://raw.githubusercontent.com/DigitalVersion/carevl/main/scripts/setup.ps1 | iex
```

### Script Capabilities

#### 1. Auto-Install Dependencies
- **winget**: Tự động cài đặt Windows Package Manager nếu thiếu
- **git**: Cài đặt qua winget
- **uv**: Cài đặt Python package manager
- **Python 3.11+**: Tự động cài đặt nếu thiếu

#### 2. Firewall Configuration
- Tự động mở Windows Firewall cho cổng 8000 (FastAPI)
- Tạo rule cho cả Inbound và Outbound
- Đặt tên rule: "CareVL FastAPI Server"

#### 3. Desktop Shortcut
- Tự động tạo shortcut trên Desktop
- Tên: **"CareVL"**
- Icon: Logo của hệ thống
- Target: Script khởi động ứng dụng

#### 4. Idempotent Behavior
Script có thể chạy nhiều lần mà không gây lỗi:
- Nếu đã có folder: `git reset --hard` và `git pull` để làm sạch
- Nếu đã có dependencies: Skip cài đặt
- Nếu đã có firewall rule: Skip tạo rule

### Security Gateway Integration
Script tích hợp với luồng Onboarding 5 bước:
1. GitHub OAuth Device Flow
2. Repository Configuration
3. Permission Gate (kiểm tra quyền truy cập)
4. Data Setup/Restore
5. PIN Setup (6 số cho offline authentication)

## Technical Details

### Script Structure
```powershell
# 1. Check and install winget
if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    # Install winget
}

# 2. Install dependencies via winget
winget install Git.Git
winget install uv

# 3. Clone/Update repository
if (Test-Path "carevl") {
    cd carevl
    git reset --hard
    git pull
} else {
    git clone https://github.com/DigitalVersion/carevl.git
    cd carevl
}

# 4. Setup Python environment
uv sync

# 5. Configure firewall
New-NetFirewallRule -DisplayName "CareVL FastAPI Server" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow

# 6. Create desktop shortcut
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$Home\Desktop\CareVL.lnk")
$Shortcut.TargetPath = "powershell.exe"
$Shortcut.Arguments = "-File `"$PWD\scripts\start.ps1`""
$Shortcut.Save()
```

## Rationale
- **Zero Config**: Người dùng không cần cài đặt gì trước
- **Idempotent**: An toàn khi chạy lại nhiều lần
- **Self-Healing**: Tự động sửa lỗi cấu hình
- **Windows-Optimized**: Tối ưu cho môi trường Windows tại trạm y tế

## Related Documents
- [04. Development Guidelines](04_Development_Guidelines.md)
- [01. FastAPI Core Architecture](01_FastAPI_Core.md)

## Troubleshooting

### Lỗi "winget not found"
- Script sẽ tự động cài winget
- Nếu thất bại, cần cài thủ công từ Microsoft Store

### Lỗi "Execution Policy"
- Đã được xử lý trong one-liner command
- Nếu vẫn lỗi: `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`

### Lỗi Firewall
- Cần chạy PowerShell với quyền Administrator
- Script sẽ tự động yêu cầu elevation nếu cần
