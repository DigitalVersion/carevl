# AWARE-SAVE Protocol: Visual Dirty State Management

## Status
**[Active]**

## Context
Trong môi trường y tế, việc mất dữ liệu do quên lưu hoặc mất điện đột ngột là rủi ro nghiêm trọng. Cần có cơ chế phòng thủ nhiều lớp để đảm bảo không có dữ liệu nào bị mất.

## Decision
Áp dụng giao thức **AWARE-SAVE** (Visual Dirty State Management) với 3 lớp phòng thủ.

## Implementation

### 1. Visual Dirty State
- **Trigger**: Bất kỳ thay đổi input nào (keyup, change event) sẽ kích hoạt `isDirty = true`
- **Visual Feedback**:
  - **Trạng thái "Chưa lưu"**: 
    - Nút Lưu đổi sang màu **Cam (#FF8C00)**
    - Hiển thị Badge **"Chưa lưu"**
  - **Trạng thái "Đã lưu"**:
    - Nút Lưu đổi sang màu **Xanh lá (#28A745)**
    - Hiển thị Icon **"✓ Đã lưu"**
    - Tự động reset sau khi HTMX response thành công

### 2. Phòng thủ 3 lớp

#### Lớp 1: beforeunload Warning
```javascript
window.addEventListener('beforeunload', (e) => {
  if (isDirty) {
    e.preventDefault();
    e.returnValue = 'Bạn có thay đổi chưa lưu. Bạn có chắc muốn rời khỏi trang?';
  }
});
```

#### Lớp 2: LocalStorage Auto-Backup
- Tự động sao lưu nháp mỗi **5 giây** vào LocalStorage
- Key format: `draft_{form_type}_{encounter_id}`
- Khi load lại trang, tự động phát hiện và hỏi khôi phục nháp
- Xóa nháp sau khi lưu thành công

```javascript
// Auto-save draft every 5 seconds
setInterval(() => {
  if (isDirty) {
    const formData = collectFormData();
    localStorage.setItem(`draft_${formType}_${encounterId}`, JSON.stringify(formData));
  }
}, 5000);
```

#### Lớp 3: Read-only Default
- Hồ sơ cũ (đã lưu) mặc định ở chế độ **khóa (read-only)**
- Phải nhấn nút **"Chỉnh sửa"** để mở khóa
- Khi mở khóa, tự động kích hoạt Visual Dirty State
- Ngăn chặn chỉnh sửa vô tình

## Rationale
- **Visual Feedback**: Người dùng luôn biết trạng thái dữ liệu của mình
- **beforeunload**: Ngăn chặn đóng tab/trình duyệt khi có thay đổi chưa lưu
- **LocalStorage Backup**: Khôi phục dữ liệu khi mất điện/sập nguồn đột ngột
- **Read-only Default**: Ngăn chặn chỉnh sửa vô tình vào hồ sơ cũ

## Technical Notes
- Sử dụng Alpine.js `x-data` để quản lý `isDirty` state
- HTMX `htmx:afterRequest` event để reset state sau khi lưu thành công
- LocalStorage có giới hạn ~5-10MB, đủ cho form data y tế

## Color Codes
- **Cam (#FF8C00)**: Cảnh báo - Chưa lưu
- **Xanh lá (#28A745)**: An toàn - Đã lưu
- **Xám (#6C757D)**: Trung lập - Không có thay đổi

## Related Documents
- [03. Web UI & HTMX Interaction](03_Web_UI_HTMX.md)
- [12. UI/UX Data Flow](12_ui_ux_flow.md)
