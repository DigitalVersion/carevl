# API Specification

## Status
[Active - Planned]

## Context
Edge app can API endpoints ro rang de:
- Frontend HTMX biet endpoint nao de call
- Backend biet response format nao
- Testing biet test gi
- Documentation de maintain

## Decision
Dinh nghia tat ca API endpoints theo RESTful conventions.

### Base URL
```
http://localhost:8000
```

### Authentication
Hien tai: Session-based (sau nay: PIN authentication)

Headers:
```
Content-Type: application/json
X-Station-ID: station-001
```

---

## API Endpoints

### 1. Health Check
```
GET /health
```

Response:
```json
{
  "status": "ok",
  "version": "2.0.0",
  "database": "connected"
}
```

---

### 2. Patient Management

#### Create Patient
```
POST /api/patients
```

Request:
```json
{
  "full_name": "Nguyen Van A",
  "birth_date": "1980-01-15",
  "gender_code": "male",
  "phone_number": "0901234567",
  "identifiers": [
    {
      "system": "CCCD",
      "value": "001234567890"
    }
  ]
}
```

Response:
```json
{
  "status": "success",
  "data": {
    "id": "uuid-123",
    "full_name": "Nguyen Van A",
    "birth_date": "1980-01-15",
    "created_at": "2026-04-28T10:30:00Z"
  }
}
```

#### Get Patient
```
GET /api/patients/{patient_id}
```

Response:
```json
{
  "status": "success",
  "data": {
    "id": "uuid-123",
    "full_name": "Nguyen Van A",
    "birth_date": "1980-01-15",
    "gender_code": "male",
    "identifiers": [
      {
        "system": "CCCD",
        "value": "001234567890"
      }
    ],
    "encounters_count": 5
  }
}
```

#### Search Patients
```
GET /api/patients?q={query}&limit=20&offset=0
```

Query params:
- `q`: Search by name, CCCD, phone
- `limit`: Results per page (default: 20)
- `offset`: Pagination offset (default: 0)

---

### 3. Encounter Management

#### Create Encounter
```
POST /api/encounters
```

Request:
```json
{
  "patient_id": "uuid-123",
  "sticker_id": "STK-001",
  "package_id": "PKG-BASIC",
  "encounter_class": "ambulatory"
}
```

Response:
```json
{
  "status": "success",
  "data": {
    "id": "enc-uuid-456",
    "patient_id": "uuid-123",
    "sticker_id": "STK-001",
    "encounter_date": "2026-04-28T10:30:00Z",
    "encounter_status": "arrived"
  }
}
```

#### Get Encounter
```
GET /api/encounters/{encounter_id}
```

#### Update Encounter Status
```
PATCH /api/encounters/{encounter_id}/status
```

Request:
```json
{
  "status": "in-progress"
}
```

#### List Encounters (Queue)
```
GET /api/encounters?status=arrived&date=2026-04-28
```

---

### 4. Observation Management

#### Create Observation
```
POST /api/observations
```

Request:
```json
{
  "encounter_id": "enc-uuid-456",
  "patient_id": "uuid-123",
  "code": "blood_pressure",
  "code_display": "Blood Pressure",
  "category": "vital-signs",
  "value_type": "string",
  "value_string": "120/80 mmHg"
}
```

#### Bulk Create Observations
```
POST /api/observations/bulk
```

Request:
```json
{
  "encounter_id": "enc-uuid-456",
  "observations": [
    {
      "code": "blood_pressure",
      "value_string": "120/80 mmHg"
    },
    {
      "code": "heart_rate",
      "value_numeric": 72,
      "unit": "bpm"
    }
  ]
}
```

---

### 5. Sync Management

#### Trigger Sync
```
POST /api/sync/trigger
```

Response:
```json
{
  "status": "success",
  "message": "Sync started",
  "job_id": "sync-job-789"
}
```

#### Get Sync Status
```
GET /api/sync/status
```

Response:
```json
{
  "status": "success",
  "data": {
    "last_sync": "2026-04-28T09:00:00Z",
    "sync_state": "synced",
    "pending_count": 0,
    "error_count": 0
  }
}
```

---

## Error Responses

### Standard Error Format
```json
{
  "status": "error",
  "message": "Human-readable error message",
  "code": "ERROR_CODE",
  "details": {
    "field": "field_name",
    "constraint": "constraint_violated"
  }
}
```

### HTTP Status Codes
- `200 OK`: Success
- `201 Created`: Resource created
- `400 Bad Request`: Validation error
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Permission denied
- `404 Not Found`: Resource not found
- `409 Conflict`: Duplicate resource
- `422 Unprocessable Entity`: Validation failed
- `500 Internal Server Error`: Server error

### Error Codes
- `VALIDATION_ERROR`: Input validation failed
- `NOT_FOUND`: Resource not found
- `DUPLICATE_IDENTIFIER`: CCCD/BHYT already exists
- `FOREIGN_KEY_ERROR`: Referenced resource not found
- `DATABASE_ERROR`: Database operation failed
- `SYNC_ERROR`: Sync operation failed
- `ENCRYPTION_ERROR`: Encryption/decryption failed

---

## UI Routes (HTMX)

### Pages
```
GET /                    -> Redirect to /login
GET /login               -> Login page
GET /intake              -> Tiep nhan moi
GET /queue               -> Luot kham (hang cho)
GET /patient-record      -> Ho so benh nhan
GET /aggregate           -> Nhap lieu aggregate
GET /results-update      -> Cap nhat ket qua
GET /reports             -> Bao cao
GET /admin/backups       -> Xuat du lieu Hub
GET /audit               -> Lien thong (Audit)
GET /settings            -> Cai dat tram
GET /about               -> Gioi thieu
```

### Partials (HTMX)
```
GET /partials/patient-card/{patient_id}
GET /partials/encounter-list?status=arrived
GET /partials/observation-form/{encounter_id}
```

---

## Validation Rules

### Patient
- `full_name`: Required, max 255 chars
- `birth_date`: Required, valid date, not future
- `gender_code`: Required, enum: male/female/other/unknown
- `phone_number`: Optional, 10-11 digits
- `identifiers.value`: Required, unique per system

### Encounter
- `patient_id`: Required, must exist
- `sticker_id`: Optional, unique if provided
- `encounter_class`: Required, enum: ambulatory/emergency/inpatient/outpatient/home
- `encounter_status`: Required, enum: planned/arrived/in-progress/finished/cancelled

### Observation
- `encounter_id`: Required, must exist
- `patient_id`: Required, must exist
- `code`: Required, max 100 chars
- `code_display`: Required, max 255 chars
- `value_type`: Required, enum: string/numeric/boolean/datetime/codeable
- At least one `value_*` field must be provided

---

## Rate Limiting
Hien tai: Khong co rate limiting (offline-first app)

Tuong lai: Neu co API public, apply rate limiting:
- 100 requests/minute per IP
- 1000 requests/hour per station

---

## Versioning
API version: `v1` (implicit in base URL)

Tuong lai: `/api/v2/...` khi co breaking changes

---

## OpenAPI/Swagger
TODO: Generate OpenAPI spec tu FastAPI:
```bash
cd edge
uv run python -c "from app.main import app; import json; print(json.dumps(app.openapi()))" > openapi.json
```

Access Swagger UI:
```
http://localhost:8000/docs
```

## Rationale
API spec ro rang giup:
- Frontend biet endpoint nao de call
- Backend biet response format
- Testing de viet test cases
- Documentation de maintain
- Onboarding dev moi nhanh hon

## Related Documents
- [01. FastAPI Core Architecture](01_FastAPI_Core.md)
- [03. Web UI & HTMX Interaction](03_Web_UI_HTMX.md)
- [09. Phase 2 Schema Spec](09_Phase2_Schema_Spec.md)
