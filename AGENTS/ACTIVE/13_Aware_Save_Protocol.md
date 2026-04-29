# AWARE-SAVE Protocol: Visual Dirty State Management

## Status
[Active - Planned]

## Context
Form nhap lieu y te co nhieu truong. Nguoi dung can biet ro:
- Co du lieu chua luu hay khong
- Dang luu hay da luu xong
- Luu that bai hay thanh cong

Neu khong co feedback ro rang:
- Nguoi dung bam "Luu" nhieu lan vi khong biet da luu chua
- Mat du lieu khi tat trinh duyet truoc khi luu
- Khong biet loi xay ra o dau khi luu that bai

## Decision
Dung AWARE-SAVE Protocol de quan ly trang thai form.

### Cac trang thai chinh
1. **CLEAN**: Form moi mo hoac vua luu xong
2. **DIRTY**: Co thay doi chua luu
3. **SAVING**: Dang gui du lieu len server
4. **SAVED**: Luu thanh cong
5. **ERROR**: Luu that bai

### Visual indicators
```
CLEAN:
- Nut "Luu": disabled, mau xam
- Khong co canh bao

DIRTY:
- Nut "Luu": enabled, mau xanh
- Hien thi: "Co thay doi chua luu" (mau vang)
- Canh bao truoc khi roi trang

SAVING:
- Nut "Luu": disabled, hien spinner
- Text: "Dang luu..."
- Khong cho roi trang

SAVED:
- Hien toast: "Da luu thanh cong" (mau xanh, 2s)
- Chuyen ve CLEAN
- Nut "Luu" disabled lai

ERROR:
- Hien toast: "Luu that bai: [loi]" (mau do, 5s)
- Nut "Luu" enabled lai
- Giu du lieu form de thu lai
```

### Implementation voi HTMX + Alpine.js

**Alpine.js state management:**
```javascript
x-data="{
  isDirty: false,
  isSaving: false,
  lastSaved: null,
  
  markDirty() {
    this.isDirty = true;
  },
  
  onSaveStart() {
    this.isSaving = true;
  },
  
  onSaveSuccess() {
    this.isDirty = false;
    this.isSaving = false;
    this.lastSaved = new Date();
    // Show success toast
  },
  
  onSaveError(msg) {
    this.isSaving = false;
    // Show error toast with msg
  }
}"
```

**Form markup:**
```html
<form 
  x-data="formState()"
  @input="markDirty()"
  hx-post="/api/save"
  hx-trigger="submit"
  @htmx:before-request="onSaveStart()"
  @htmx:after-request="onSaveSuccess()"
  @htmx:response-error="onSaveError($event.detail.xhr.responseText)"
>
  <!-- Dirty indicator -->
  <div x-show="isDirty && !isSaving" class="alert alert-warning">
    <span>⚠️ Co thay doi chua luu</span>
  </div>
  
  <!-- Saving indicator -->
  <div x-show="isSaving" class="alert alert-info">
    <span class="spinner"></span> Dang luu...
  </div>
  
  <!-- Form fields -->
  <input type="text" name="field1" @input="markDirty()">
  
  <!-- Save button -->
  <button 
    type="submit"
    :disabled="!isDirty || isSaving"
    :class="{'btn-primary': isDirty, 'btn-disabled': !isDirty}"
  >
    <span x-show="!isSaving">Luu</span>
    <span x-show="isSaving">Dang luu...</span>
  </button>
  
  <!-- Last saved timestamp -->
  <small x-show="lastSaved" class="text-muted">
    Lan luu cuoi: <span x-text="formatTime(lastSaved)"></span>
  </small>
</form>
```

**Prevent navigation khi DIRTY:**
```javascript
window.addEventListener('beforeunload', (e) => {
  if (Alpine.store('formState').isDirty) {
    e.preventDefault();
    e.returnValue = 'Ban co thay doi chua luu. Ban co chac muon roi trang?';
  }
});
```

### Backend response format
Server phai tra ve JSON ro rang:

**Success:**
```json
{
  "status": "success",
  "message": "Da luu thanh cong",
  "data": {
    "id": "uuid-123",
    "updated_at": "2026-04-28T10:30:00Z"
  }
}
```

**Error:**
```json
{
  "status": "error",
  "message": "Luu that bai: Thieu truong bat buoc 'CCCD'",
  "errors": {
    "cccd": ["Truong nay bat buoc"]
  }
}
```

### Auto-save (optional)
Doi voi form dai, co the bat auto-save:
- Debounce 3s sau khi ngung go
- Chi auto-save khi DIRTY
- Hien thi "Tu dong luu..." thay vi "Dang luu..."
- Khong disable form khi auto-save

```javascript
let autoSaveTimer;
function scheduleAutoSave() {
  clearTimeout(autoSaveTimer);
  autoSaveTimer = setTimeout(() => {
    if (isDirty && !isSaving) {
      htmx.trigger('#form', 'submit');
    }
  }, 3000);
}
```

### Offline handling
Khi mat mang:
- Luu vao `localStorage` tam thoi
- Hien thi: "Khong co mang. Du lieu luu tam thoi."
- Khi co mang lai, tu dong dong bo
- Hien thi so luong form chua dong bo

### Testing checklist
- [ ] Nhap du lieu -> nut "Luu" enabled
- [ ] Bam "Luu" -> hien "Dang luu..."
- [ ] Luu xong -> hien toast "Da luu thanh cong"
- [ ] Luu xong -> nut "Luu" disabled
- [ ] Luu loi -> hien toast loi, nut van enabled
- [ ] Co DIRTY -> canh bao truoc khi roi trang
- [ ] Khong DIRTY -> khong canh bao khi roi trang
- [ ] Auto-save (neu co) -> luu sau 3s ngung go
- [ ] Offline -> luu vao localStorage

## Rationale
Visual feedback ro rang giam lo lang cua nguoi dung, giam loi mat du lieu, va tang tin tuong vao he thong. HTMX + Alpine.js du nhe de implement ma khong can React hay Vue. Protocol nay ap dung cho tat ca form trong he thong: tiep nhan, luot kham, ho so, nhap lieu, ket qua.

## Related Documents
- [03. Web UI & HTMX Interaction](03_Web_UI_HTMX.md)
- [12. UI/UX Data Flow: Intake to Delayed Results](12_ui_ux_flow.md)
- [../FEATURES/1_tiep_nhan_moi.md](../FEATURES/1_tiep_nhan_moi.md)
- [../FEATURES/3_ho_so_benh_nhan.md](../FEATURES/3_ho_so_benh_nhan.md)
- [../FEATURES/5_cap_nhat_ket_qua.md](../FEATURES/5_cap_nhat_ket_qua.md)
