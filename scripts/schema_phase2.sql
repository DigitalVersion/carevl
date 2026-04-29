-- ============================================================================
-- CareVL Phase 2 Schema - FHIR-Aligned SQLite Database
-- ============================================================================
-- Version: 2.0.0
-- Date: 2026-04-28
-- Description: Complete schema for Edge app with FHIR-aligned structure
-- Reference: AGENTS/ACTIVE/09_Phase2_Schema_Spec.md
-- ============================================================================

-- Enable foreign keys
PRAGMA foreign_keys = ON;

-- Enable WAL mode for better concurrency
PRAGMA journal_mode = WAL;

-- ============================================================================
-- CORE TABLES (Bang loi)
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Table: patients
-- Purpose: Thong tin co ban nguoi benh
-- FHIR: Patient resource
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS patients (
    -- Primary key: UUID v4
    id TEXT PRIMARY KEY NOT NULL,
    
    -- Demographics
    full_name TEXT NOT NULL,
    birth_date DATE NOT NULL,
    gender_code TEXT CHECK(gender_code IN ('male', 'female', 'other', 'unknown')),
    
    -- Contact
    phone_number TEXT,
    email TEXT,
    address_line TEXT,
    address_district TEXT,
    address_province TEXT,
    
    -- Metadata
    station_id TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Soft delete
    deleted_at TIMESTAMP,
    
    -- Raw data for migration/audit
    raw_json TEXT
);

CREATE INDEX idx_patients_full_name ON patients(full_name);
CREATE INDEX idx_patients_birth_date ON patients(birth_date);
CREATE INDEX idx_patients_station_id ON patients(station_id);
CREATE INDEX idx_patients_deleted_at ON patients(deleted_at);

-- ----------------------------------------------------------------------------
-- Table: patient_identifiers
-- Purpose: CCCD, VNeID, BHYT, ma noi bo
-- FHIR: Patient.identifier
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS patient_identifiers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Foreign key
    patient_id TEXT NOT NULL,
    
    -- Identifier system: 'CCCD', 'VNeID', 'BHYT', 'MRN', 'passport'
    system TEXT NOT NULL,
    
    -- Identifier value
    value TEXT NOT NULL,
    
    -- Period of validity
    valid_from DATE,
    valid_until DATE,
    
    -- Metadata
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
    UNIQUE(system, value)
);

CREATE INDEX idx_patient_identifiers_patient_id ON patient_identifiers(patient_id);
CREATE INDEX idx_patient_identifiers_value ON patient_identifiers(value);
CREATE INDEX idx_patient_identifiers_system ON patient_identifiers(system);

-- ----------------------------------------------------------------------------
-- Table: encounters
-- Purpose: Moi dong la mot luot kham
-- FHIR: Encounter resource
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS encounters (
    -- Primary key: UUID v4
    id TEXT PRIMARY KEY NOT NULL,
    
    -- Foreign key
    patient_id TEXT NOT NULL,
    
    -- Business identifier
    sticker_id TEXT UNIQUE,
    
    -- Encounter details
    encounter_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    encounter_class TEXT CHECK(encounter_class IN ('ambulatory', 'emergency', 'inpatient', 'outpatient', 'home')) DEFAULT 'ambulatory',
    encounter_status TEXT CHECK(encounter_status IN ('planned', 'arrived', 'in-progress', 'finished', 'cancelled')) DEFAULT 'arrived',
    
    -- Package/program
    package_id TEXT,
    package_name TEXT,
    
    -- Location
    station_id TEXT NOT NULL,
    commune_code TEXT,
    
    -- Summary
    summary_text TEXT,
    classification_display TEXT,
    
    -- Sync state
    sync_state TEXT CHECK(sync_state IN ('pending', 'synced', 'error')) DEFAULT 'pending',
    synced_at TIMESTAMP,
    
    -- Metadata
    author TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Soft delete
    deleted_at TIMESTAMP,
    
    -- Raw data for migration/audit
    raw_json TEXT,
    
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
);

CREATE INDEX idx_encounters_patient_id ON encounters(patient_id);
CREATE INDEX idx_encounters_sticker_id ON encounters(sticker_id);
CREATE INDEX idx_encounters_encounter_date ON encounters(encounter_date);
CREATE INDEX idx_encounters_station_id ON encounters(station_id);
CREATE INDEX idx_encounters_sync_state ON encounters(sync_state);
CREATE INDEX idx_encounters_patient_date ON encounters(patient_id, encounter_date);
CREATE INDEX idx_encounters_station_date ON encounters(station_id, encounter_date);

-- ----------------------------------------------------------------------------
-- Table: encounter_participants
-- Purpose: Bac si, dieu duong, nguoi nhap, nguoi duyet
-- FHIR: Encounter.participant
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS encounter_participants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Foreign key
    encounter_id TEXT NOT NULL,
    
    -- Participant details
    participant_type TEXT CHECK(participant_type IN ('doctor', 'nurse', 'data_entry', 'reviewer', 'admin')) NOT NULL,
    participant_name TEXT NOT NULL,
    participant_id TEXT,
    
    -- Period
    period_start TIMESTAMP,
    period_end TIMESTAMP,
    
    -- Metadata
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (encounter_id) REFERENCES encounters(id) ON DELETE CASCADE
);

CREATE INDEX idx_encounter_participants_encounter_id ON encounter_participants(encounter_id);
CREATE INDEX idx_encounter_participants_type ON encounter_participants(participant_type);

-- ----------------------------------------------------------------------------
-- Table: observations
-- Purpose: Sinh hieu, can lam sang, xet nghiem
-- FHIR: Observation resource
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS observations (
    -- Primary key: UUID v4
    id TEXT PRIMARY KEY NOT NULL,
    
    -- Foreign key
    encounter_id TEXT NOT NULL,
    patient_id TEXT NOT NULL,
    
    -- Observation code (LOINC, SNOMED, local)
    code_system TEXT NOT NULL DEFAULT 'local',
    code TEXT NOT NULL,
    code_display TEXT NOT NULL,
    
    -- Category: 'vital-signs', 'laboratory', 'imaging', 'exam'
    category TEXT,
    
    -- Value (polymorphic)
    value_type TEXT CHECK(value_type IN ('string', 'numeric', 'boolean', 'datetime', 'codeable')) NOT NULL,
    value_string TEXT,
    value_numeric REAL,
    value_boolean INTEGER CHECK(value_boolean IN (0, 1)),
    value_datetime TIMESTAMP,
    value_code TEXT,
    value_code_display TEXT,
    
    -- Unit
    unit TEXT,
    unit_system TEXT,
    
    -- Reference range
    reference_range_low REAL,
    reference_range_high REAL,
    reference_range_text TEXT,
    
    -- Interpretation: 'normal', 'abnormal', 'critical'
    interpretation TEXT,
    
    -- Source tracking (for migration from dynamic forms)
    source_section_id TEXT,
    source_field_id TEXT,
    
    -- Metadata
    effective_datetime TIMESTAMP,
    issued_datetime TIMESTAMP,
    performer TEXT,
    station_id TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Soft delete
    deleted_at TIMESTAMP,
    
    FOREIGN KEY (encounter_id) REFERENCES encounters(id) ON DELETE CASCADE,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
);

CREATE INDEX idx_observations_encounter_id ON observations(encounter_id);
CREATE INDEX idx_observations_patient_id ON observations(patient_id);
CREATE INDEX idx_observations_code ON observations(code);
CREATE INDEX idx_observations_category ON observations(category);
CREATE INDEX idx_observations_source_section ON observations(source_section_id);
CREATE INDEX idx_observations_source_field ON observations(source_field_id);
CREATE INDEX idx_observations_effective_datetime ON observations(effective_datetime);

-- ----------------------------------------------------------------------------
-- Table: conditions
-- Purpose: Tien su, chan doan, ket luan
-- FHIR: Condition resource
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS conditions (
    -- Primary key: UUID v4
    id TEXT PRIMARY KEY NOT NULL,
    
    -- Foreign key
    patient_id TEXT NOT NULL,
    encounter_id TEXT,
    
    -- Condition code (ICD-10, SNOMED, local)
    code_system TEXT NOT NULL DEFAULT 'local',
    code TEXT NOT NULL,
    code_display TEXT NOT NULL,
    
    -- Category: 'problem-list-item', 'encounter-diagnosis', 'medical-history'
    category TEXT,
    
    -- Clinical status: 'active', 'resolved', 'inactive'
    clinical_status TEXT CHECK(clinical_status IN ('active', 'resolved', 'inactive', 'remission')) DEFAULT 'active',
    
    -- Verification status: 'confirmed', 'provisional', 'differential'
    verification_status TEXT CHECK(verification_status IN ('confirmed', 'provisional', 'differential', 'refuted')) DEFAULT 'confirmed',
    
    -- Severity: 'mild', 'moderate', 'severe'
    severity TEXT CHECK(severity IN ('mild', 'moderate', 'severe')),
    
    -- Onset
    onset_datetime TIMESTAMP,
    onset_string TEXT,
    
    -- Abatement (resolution)
    abatement_datetime TIMESTAMP,
    abatement_string TEXT,
    
    -- Note
    note TEXT,
    
    -- Metadata
    recorded_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    recorder TEXT,
    station_id TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Soft delete
    deleted_at TIMESTAMP,
    
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
    FOREIGN KEY (encounter_id) REFERENCES encounters(id) ON DELETE SET NULL
);

CREATE INDEX idx_conditions_patient_id ON conditions(patient_id);
CREATE INDEX idx_conditions_encounter_id ON conditions(encounter_id);
CREATE INDEX idx_conditions_code ON conditions(code);
CREATE INDEX idx_conditions_category ON conditions(category);
CREATE INDEX idx_conditions_clinical_status ON conditions(clinical_status);

-- ----------------------------------------------------------------------------
-- Table: questionnaires
-- Purpose: Version hoa template_form.json
-- FHIR: Questionnaire resource
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS questionnaires (
    -- Primary key: UUID v4
    id TEXT PRIMARY KEY NOT NULL,
    
    -- Questionnaire details
    title TEXT NOT NULL,
    version TEXT NOT NULL,
    status TEXT CHECK(status IN ('draft', 'active', 'retired')) DEFAULT 'active',
    
    -- Full questionnaire definition (JSON)
    definition_json TEXT NOT NULL,
    
    -- Metadata
    station_id TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(title, version)
);

CREATE INDEX idx_questionnaires_title ON questionnaires(title);
CREATE INDEX idx_questionnaires_version ON questionnaires(version);
CREATE INDEX idx_questionnaires_status ON questionnaires(status);

-- ----------------------------------------------------------------------------
-- Table: questionnaire_responses
-- Purpose: Giu cau tra loi day du theo form
-- FHIR: QuestionnaireResponse resource
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS questionnaire_responses (
    -- Primary key: UUID v4
    id TEXT PRIMARY KEY NOT NULL,
    
    -- Foreign keys
    questionnaire_id TEXT NOT NULL,
    encounter_id TEXT NOT NULL,
    patient_id TEXT NOT NULL,
    
    -- Response status: 'in-progress', 'completed', 'amended'
    status TEXT CHECK(status IN ('in-progress', 'completed', 'amended')) DEFAULT 'in-progress',
    
    -- Full response (JSON)
    response_json TEXT NOT NULL,
    
    -- Metadata
    authored_datetime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    author TEXT,
    station_id TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Soft delete
    deleted_at TIMESTAMP,
    
    FOREIGN KEY (questionnaire_id) REFERENCES questionnaires(id) ON DELETE RESTRICT,
    FOREIGN KEY (encounter_id) REFERENCES encounters(id) ON DELETE CASCADE,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
);

CREATE INDEX idx_questionnaire_responses_questionnaire_id ON questionnaire_responses(questionnaire_id);
CREATE INDEX idx_questionnaire_responses_encounter_id ON questionnaire_responses(encounter_id);
CREATE INDEX idx_questionnaire_responses_patient_id ON questionnaire_responses(patient_id);
CREATE INDEX idx_questionnaire_responses_status ON questionnaire_responses(status);

-- ============================================================================
-- SUPPORTING TABLES (Bang phu bat buoc)
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Table: audit_events
-- Purpose: Truy vet tao/sua/xoa, migrate, sync
-- FHIR: AuditEvent resource
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS audit_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Event details
    event_type TEXT CHECK(event_type IN ('create', 'update', 'delete', 'migrate', 'sync', 'export', 'import', 'login', 'logout')) NOT NULL,
    event_action TEXT,
    event_outcome TEXT CHECK(event_outcome IN ('success', 'failure', 'warning')),
    
    -- Resource reference
    resource_type TEXT,
    resource_id TEXT,
    
    -- Agent (who did it)
    agent_type TEXT CHECK(agent_type IN ('user', 'system', 'device')),
    agent_name TEXT,
    agent_id TEXT,
    
    -- Source (where it happened)
    source_station_id TEXT,
    source_ip TEXT,
    
    -- Details
    description TEXT,
    changes_json TEXT,
    
    -- Timestamp
    recorded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_events_event_type ON audit_events(event_type);
CREATE INDEX idx_audit_events_resource_type ON audit_events(resource_type);
CREATE INDEX idx_audit_events_resource_id ON audit_events(resource_id);
CREATE INDEX idx_audit_events_agent_id ON audit_events(agent_id);
CREATE INDEX idx_audit_events_recorded_at ON audit_events(recorded_at);

-- ============================================================================
-- EXTENDED TABLES (Bang phu mo rong)
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Table: code_map_local
-- Purpose: Map local codes to standard terminologies
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS code_map_local (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Local code
    local_code TEXT NOT NULL,
    local_display TEXT NOT NULL,
    local_system TEXT DEFAULT 'local',
    
    -- Target code
    target_system TEXT CHECK(target_system IN ('loinc', 'snomed', 'icd10', 'rxnorm')),
    target_code TEXT,
    target_display TEXT,
    
    -- Mapping details
    equivalence TEXT CHECK(equivalence IN ('equivalent', 'wider', 'narrower', 'inexact', 'unmatched')) DEFAULT 'equivalent',
    comment TEXT,
    
    -- Metadata
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(local_code, target_system)
);

CREATE INDEX idx_code_map_local_code ON code_map_local(local_code);
CREATE INDEX idx_code_map_target_code ON code_map_local(target_code);

-- ----------------------------------------------------------------------------
-- Table: attachments
-- Purpose: Store file references (images, PDFs, etc.)
-- FHIR: DocumentReference, Media
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS attachments (
    -- Primary key: UUID v4
    id TEXT PRIMARY KEY NOT NULL,
    
    -- Foreign keys (polymorphic)
    resource_type TEXT CHECK(resource_type IN ('patient', 'encounter', 'observation', 'condition')) NOT NULL,
    resource_id TEXT NOT NULL,
    
    -- File details
    content_type TEXT NOT NULL,
    file_name TEXT NOT NULL,
    file_size INTEGER,
    file_path TEXT NOT NULL,
    
    -- Hash for integrity
    file_hash TEXT,
    
    -- Description
    title TEXT,
    description TEXT,
    
    -- Metadata
    station_id TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    
    -- Soft delete
    deleted_at TIMESTAMP
);

CREATE INDEX idx_attachments_resource ON attachments(resource_type, resource_id);
CREATE INDEX idx_attachments_station_id ON attachments(station_id);

-- ============================================================================
-- LEGACY TABLES (Keep for backward compatibility during migration)
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Table: diagnostic_reports (existing)
-- Purpose: Delayed results (Lab, X-Ray) - will be migrated to observations
-- ----------------------------------------------------------------------------
-- Keep existing table structure for now

-- ----------------------------------------------------------------------------
-- Table: measure_reports (existing)
-- Purpose: Aggregate data - separate from patient records
-- ----------------------------------------------------------------------------
-- Keep existing table structure for now

-- ----------------------------------------------------------------------------
-- Table: system_config (existing)
-- Purpose: System configuration
-- ----------------------------------------------------------------------------
-- Keep existing table structure for now

-- ============================================================================
-- METADATA TABLE
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Table: schema_version
-- Purpose: Track schema migrations
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS schema_version (
    version TEXT PRIMARY KEY NOT NULL,
    applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

-- Insert initial version
INSERT OR IGNORE INTO schema_version (version, description) 
VALUES ('2.0.0', 'Phase 2 FHIR-aligned schema');

-- ============================================================================
-- TRIGGERS FOR updated_at
-- ============================================================================

-- Patients
CREATE TRIGGER IF NOT EXISTS trigger_patients_updated_at
AFTER UPDATE ON patients
FOR EACH ROW
BEGIN
    UPDATE patients SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Encounters
CREATE TRIGGER IF NOT EXISTS trigger_encounters_updated_at
AFTER UPDATE ON encounters
FOR EACH ROW
BEGIN
    UPDATE encounters SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Observations
CREATE TRIGGER IF NOT EXISTS trigger_observations_updated_at
AFTER UPDATE ON observations
FOR EACH ROW
BEGIN
    UPDATE observations SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Conditions
CREATE TRIGGER IF NOT EXISTS trigger_conditions_updated_at
AFTER UPDATE ON conditions
FOR EACH ROW
BEGIN
    UPDATE conditions SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Questionnaire Responses
CREATE TRIGGER IF NOT EXISTS trigger_questionnaire_responses_updated_at
AFTER UPDATE ON questionnaire_responses
FOR EACH ROW
BEGIN
    UPDATE questionnaire_responses SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Questionnaires
CREATE TRIGGER IF NOT EXISTS trigger_questionnaires_updated_at
AFTER UPDATE ON questionnaires
FOR EACH ROW
BEGIN
    UPDATE questionnaires SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Code Map Local
CREATE TRIGGER IF NOT EXISTS trigger_code_map_local_updated_at
AFTER UPDATE ON code_map_local
FOR EACH ROW
BEGIN
    UPDATE code_map_local SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- View: Complete patient info with identifiers
CREATE VIEW IF NOT EXISTS v_patients_complete AS
SELECT 
    p.*,
    GROUP_CONCAT(
        pi.system || ':' || pi.value, '; '
    ) as identifiers
FROM patients p
LEFT JOIN patient_identifiers pi ON p.id = pi.patient_id
WHERE p.deleted_at IS NULL
GROUP BY p.id;

-- View: Encounters with patient info
CREATE VIEW IF NOT EXISTS v_encounters_with_patient AS
SELECT 
    e.*,
    p.full_name as patient_name,
    p.birth_date as patient_birth_date,
    p.gender_code as patient_gender
FROM encounters e
JOIN patients p ON e.patient_id = p.id
WHERE e.deleted_at IS NULL AND p.deleted_at IS NULL;

-- View: Latest observations per encounter
CREATE VIEW IF NOT EXISTS v_observations_latest AS
SELECT 
    o.*,
    e.encounter_date,
    p.full_name as patient_name
FROM observations o
JOIN encounters e ON o.encounter_id = e.id
JOIN patients p ON o.patient_id = p.id
WHERE o.deleted_at IS NULL
ORDER BY o.effective_datetime DESC;

-- ============================================================================
-- SAMPLE DATA FOR TESTING
-- ============================================================================

-- Insert sample questionnaire
INSERT OR IGNORE INTO questionnaires (id, title, version, status, definition_json, created_at)
VALUES (
    'q-default-v1',
    'Default Health Screening Form',
    '1.0.0',
    'active',
    '{"sections": [{"id": "demographics", "title": "Thông tin cơ bản"}]}',
    CURRENT_TIMESTAMP
);

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
