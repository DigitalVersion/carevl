# Phase 2 Migration Guide

## Status
[Active - Planned]

## Context
Phase 1 dung JSON phang luu trong bang `records`. Phase 2 chuyen sang FHIR-aligned relational schema. Can migrate du lieu cu sang cau truc moi ma khong mat thong tin.

## Decision
Dung migration script Python de chuyen du lieu tu Phase 1 sang Phase 2.

### Pre-migration checklist
- [ ] Backup database hien tai: `cp data/carevl.db data/carevl_backup_$(date +%Y%m%d).db`
- [ ] Chay script tren database test truoc
- [ ] Xac nhan `station_id` dung
- [ ] Kiem tra disk space du (can ~2x kich thuoc DB hien tai)
- [ ] Dong tat ca ung dung dang truy cap DB

### Migration steps

**1. Backup database:**
```bash
# Windows
copy data\carevl.db data\carevl_backup_%date:~-4,4%%date:~-10,2%%date:~-7,2%.db

# Linux/Mac
cp data/carevl.db data/carevl_backup_$(date +%Y%m%d).db
```

**2. Apply Phase 2 schema:**
```bash
# Create new tables (existing tables won't be affected)
sqlite3 data/carevl.db < scripts/schema_phase2.sql
```

**3. Run migration script:**
```bash
uv run python scripts/migrate_to_phase2.py data/carevl.db station-001
```

**4. Verify migration:**
```bash
# Check record counts
sqlite3 data/carevl.db "SELECT COUNT(*) FROM patients;"
sqlite3 data/carevl.db "SELECT COUNT(*) FROM encounters;"
sqlite3 data/carevl.db "SELECT COUNT(*) FROM observations;"
sqlite3 data/carevl.db "SELECT COUNT(*) FROM audit_events WHERE event_type='migrate';"
```

**5. Test application:**
```bash
uv run uvicorn app.main:app --reload
# Open browser, test features
```

**6. Cleanup old tables (optional):**
```sql
-- Only after confirming migration success
-- DROP TABLE records;
-- Keep for now as backup
```

### Migration logic

**Patient deduplication:**
1. Tim patient theo CCCD
2. Neu chua co, tao moi
3. Neu da co, dung patient_id cu
4. Luu CCCD vao `patient_identifiers`

**Encounter mapping:**
- `record.id` -> `encounters.id`
- `record.sticker_id` -> `encounters.sticker_id`
- `record.package_id` -> `encounters.package_id`
- `record.author` -> `encounters.author` + `encounter_participants`
- `record.synced` -> `encounters.sync_state`

**Observation extraction:**
- Quet `record.data` tim cac truong y khoa
- Tach thanh `observations` voi `code`, `value`, `unit`
- Gan `source_section_id` va `source_field_id` de truy vet

**Condition extraction:**
- Tach `diagnosis`, `medical_history` thanh `conditions`
- Gan `category` phu hop
- Luu `clinical_status` va `verification_status`

**QuestionnaireResponse:**
- Luu toan bo `record.data` vao `response_json`
- Link voi `questionnaire_id` mac dinh
- Giu nguyen context form de audit

**Audit trail:**
- Moi record migrate tao `audit_event` voi `event_type='migrate'`
- Luu `resource_id` va `description`
- Giup truy vet nguon goc du lieu

### Rollback procedure

Neu migration loi:
```bash
# Stop application
# Restore backup
copy data\carevl_backup_YYYYMMDD.db data\carevl.db

# Restart application
uv run uvicorn app.main:app --reload
```

### Post-migration tasks

**1. Update application code:**
- Sua API endpoints doc tu bang moi
- Cap nhat UI hien thi du lieu tu bang moi
- Test tat ca features

**2. Verify data integrity:**
```sql
-- Check orphaned records
SELECT COUNT(*) FROM encounters WHERE patient_id NOT IN (SELECT id FROM patients);
SELECT COUNT(*) FROM observations WHERE encounter_id NOT IN (SELECT id FROM encounters);

-- Check missing required fields
SELECT COUNT(*) FROM patients WHERE full_name IS NULL OR birth_date IS NULL;
SELECT COUNT(*) FROM encounters WHERE patient_id IS NULL OR station_id IS NULL;
```

**3. Performance tuning:**
```sql
-- Rebuild indexes
REINDEX;

-- Analyze tables
ANALYZE;

-- Check database size
SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size();
```

**4. Update documentation:**
- Cap nhat API docs
- Cap nhat user guide
- Cap nhat training materials

### Common issues

**Issue: "UNIQUE constraint failed: patient_identifiers.system, value"**
- Nguyen nhan: Trung CCCD
- Giai phap: Kiem tra va merge patients trung

**Issue: "FOREIGN KEY constraint failed"**
- Nguyen nhan: patient_id hoac encounter_id khong ton tai
- Giai phap: Kiem tra thu tu migrate, dam bao patient truoc encounter

**Issue: Migration qua cham**
- Nguyen nhan: Nhieu record, index cham
- Giai phap: Tat index truoc migrate, bat lai sau

**Issue: Out of disk space**
- Nguyen nhan: DB lon, can 2x space
- Giai phap: Don disk hoac migrate tren may khac

### Testing migration

**Test voi sample data:**
```bash
# Create test database
cp data/carevl.db data/carevl_test.db

# Run migration on test
uv run python scripts/migrate_to_phase2.py data/carevl_test.db station-test

# Verify
sqlite3 data/carevl_test.db "SELECT * FROM patients LIMIT 5;"
```

**Test queries:**
```sql
-- Get patient with all encounters
SELECT p.full_name, e.encounter_date, e.summary_text
FROM patients p
JOIN encounters e ON p.id = e.patient_id
WHERE p.id = 'patient-uuid';

-- Get observations for encounter
SELECT o.code_display, o.value_numeric, o.unit
FROM observations o
WHERE o.encounter_id = 'encounter-uuid';

-- Get audit trail
SELECT event_type, resource_type, description, recorded_at
FROM audit_events
WHERE resource_id = 'encounter-uuid'
ORDER BY recorded_at DESC;
```

## Rationale
Migration script tu dong hoa quy trinh, giam loi tay, va ghi audit trail day du. Backup truoc khi migrate dam bao co the rollback neu can. Test tren database test truoc giup phat hien van de som.

## Related Documents
- [09. Phase 2 Schema Spec](09_Phase2_Schema_Spec.md)
- [02. SQLite Security & Snapshots](02_SQLite_Security.md)
- [16. Testing Guidelines](16_Testing_Guidelines.md)
