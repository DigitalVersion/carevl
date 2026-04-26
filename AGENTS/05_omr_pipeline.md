# OMR Pipeline (Legacy)

Các module OMR chạy độc lập, chưa tích hợp thành menu chính trong app:

```powershell
# Tạo PDF từ CCCD
python -m legacy.modules.omr_form_gen --cccd 001286001234 --package nct --output form.pdf

# Đọc batch scan
python -m legacy.modules.omr_reader --input scans/ --output results/ --package nct --json results.json

# Map và lưu
python -m legacy.modules.omr_bridge --input results.json --package nct --save --author bacsi01
```
