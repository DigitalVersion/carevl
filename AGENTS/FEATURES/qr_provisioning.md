# Feature: QR Code Provisioning (Thẻ bài điện tử)

## Status
[Planned]

- UI: chua xong
- Backend: chua xong
- Van hanh: chua mo

## Context
Benh nhan can mang theo giay to kham benh nhieu lan. Giay de mat, de rach, kho quan ly. Tram can cach nhanh de dinh danh benh nhan khi tro lai kham.

Yeu cau:
- Benh nhan quet QR tren dien thoai de hien thong tin
- Tram quet QR de load ho so nhanh
- Khong can internet de quet
- Du lieu trong QR phai du de dinh danh nhung khong qua nhieu

## Decision
Dung QR Code lam "the bai dien tu" cho benh nhan.

### QR Code structure
Luu du lieu dinh danh toi thieu trong QR:
```json
{
  "patient_id": "uuid-123",
  "full_name": "Nguyen Van A",
  "birth_date": "1980-01-15",
  "cccd": "001234567890",
  "station_id": "station-001",
  "issued_at": "2026-04-28T10:30:00Z"
}
```

Encode thanh Base64 URL-safe, roi tao QR Code.

### Use cases

**1. Benh nhan xem thong tin:**
- Benh nhan mo camera dien thoai
- Quet QR Code
- Hien thi thong tin co ban: ten, ngay sinh, ma benh nhan
- Khong can internet, chi can QR reader app

**2. Tram load ho so nhanh:**
- Nhan vien quet QR bang camera may tinh hoac dien thoai
- He thong tim `patient_id` trong DB
- Load ho so benh nhan
- Hien thi lich su kham, ket qua xet nghiem

**3. Tram khac tra cuu:**
- Benh nhan den tram khac
- Tram moi quet QR
- Neu khong co ho so local -> hien thi thong tin tu QR
- Tao encounter moi voi thong tin da co

### Implementation

**Generate QR khi tiep nhan:**
```python
import qrcode
import json
import base64

def generate_patient_qr(patient):
    data = {
        "patient_id": patient.id,
        "full_name": patient.full_name,
        "birth_date": patient.birth_date.isoformat(),
        "cccd": patient.cccd,
        "station_id": patient.station_id,
        "issued_at": datetime.now().isoformat()
    }
    
    # Encode to Base64 URL-safe
    json_str = json.dumps(data)
    encoded = base64.urlsafe_b64encode(json_str.encode()).decode()
    
    # Generate QR Code
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(encoded)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    return img
```

**Scan QR va parse:**
```javascript
// Frontend: dung html5-qrcode
const html5QrCode = new Html5Qrcode("reader");
html5QrCode.start(
  { facingMode: "environment" },
  { fps: 10, qrbox: 250 },
  (decodedText) => {
    // Decode Base64
    const jsonStr = atob(decodedText);
    const data = JSON.parse(jsonStr);
    
    // Send to backend to load patient
    htmx.ajax('POST', '/api/load-patient', {
      values: { patient_id: data.patient_id }
    });
  }
);
```

**Backend endpoint:**
```python
@router.post("/api/load-patient")
async def load_patient(patient_id: str, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    
    if not patient:
        # Neu khong co local, tao patient moi tu QR data
        # (can gui them data tu frontend)
        raise HTTPException(404, "Patient not found")
    
    # Load encounters, observations, conditions
    encounters = db.query(Encounter).filter(
        Encounter.patient_id == patient_id
    ).all()
    
    return {
        "patient": patient,
        "encounters": encounters
    }
```

### UI Flow

**1. Tiep nhan moi:**
- Nhap CCCD, ten, ngay sinh
- Tao Patient record
- Generate QR Code
- In QR Code len giay A6 hoac sticker
- Trao cho benh nhan

**2. Kham lai:**
- Benh nhan den, dua QR
- Nhan vien quet QR
- He thong load ho so
- Tao encounter moi

**3. Xem thong tin (benh nhan):**
- Benh nhan mo app quet QR bat ky
- Quet QR tren giay
- Hien thi thong tin co ban
- Khong can dang nhap

### Security considerations

**Du lieu trong QR:**
- Chi luu thong tin dinh danh co ban
- Khong luu du lieu y te nhay cam
- Khong luu password hay token
- Co the them checksum de validate

**Validate QR:**
- Kiem tra `issued_at` khong qua cu (> 1 nam)
- Kiem tra `station_id` hop le
- Kiem tra format JSON dung

**Privacy:**
- QR chi hien thong tin co ban
- Du lieu y te chi load khi quet tai tram
- Benh nhan tu quet chi thay ten, ngay sinh, ma BN

### Print options

**Option 1: In len giay A6:**
- QR Code lon, de quet
- Kem thong tin text: ten, ngay sinh, ma BN
- Benh nhan cat dan vao so kham benh

**Option 2: In len sticker:**
- Sticker nho, dan vao the nhua
- Benh nhan mang theo vi
- Ben hon, khong de rach

**Option 3: Luu vao dien thoai:**
- Benh nhan chup anh QR
- Hoac luu file PNG vao thu vien anh
- Hien thi khi can

### Alternative: Deep link
Thay vi chi QR, co the dung deep link:
```
carevl://patient/uuid-123
```

Neu benh nhan co app CareVL tren dien thoai, quet QR se mo app va hien ho so.

### Testing checklist
- [ ] Generate QR tu patient record
- [ ] Scan QR bang camera
- [ ] Parse Base64 va JSON
- [ ] Load patient tu DB
- [ ] Hien thi ho so
- [ ] In QR len giay
- [ ] Test voi QR cu (> 1 nam)
- [ ] Test voi QR sai format
- [ ] Test voi patient_id khong ton tai

## Rationale
QR Code la cach don gian, re, va khong can internet de dinh danh benh nhan. Benh nhan chi can mang mot manh giay nho hoac chup anh luu dien thoai. Tram quet nhanh hon nhap tay, it loi hon, va ho tro ca truong hop benh nhan den tram khac.

## Related Endpoints
- `POST /api/generate-qr`
- `POST /api/load-patient`
- `GET /patient-qr/{patient_id}`

## FHIR/IHE Mapping
- Resources: `Patient`
- Mapping: QR chua `patient_id` de link voi Patient resource

## Persona Impact
- Persona A (Tiep nhan): generate va in QR
- Persona B (Lam sang): quet QR de load ho so
- Persona C (Nhap lieu): quet QR de gan ket qua
- Benh nhan: mang QR, quet de xem thong tin

## Mockup Assets
- `qr_card_sample.png`: mau the QR in ra
- `qr_scan_ui.png`: man hinh quet QR

## Related Documents
- [Sidebar UI Architecture](sidebar_ui.md)
- [1. Tiep nhan moi](1_tiep_nhan_moi.md)
- [3. Ho so benh nhan](3_ho_so_benh_nhan.md)
- [12. UI/UX Data Flow: Intake to Delayed Results](../ACTIVE/12_ui_ux_flow.md)
