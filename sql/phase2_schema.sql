PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS schema_meta (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

INSERT OR REPLACE INTO schema_meta(key, value)
VALUES ('phase2_schema_version', '1.0.0');

CREATE TABLE IF NOT EXISTS patients (
    id TEXT PRIMARY KEY,
    active INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0, 1)),
    full_name TEXT NOT NULL,
    family_name TEXT,
    given_name TEXT,
    birth_date TEXT,
    gender_code TEXT CHECK (gender_code IN ('male', 'female', 'other', 'unknown') OR gender_code IS NULL),
    gender_text TEXT,
    target_group_code TEXT NOT NULL,
    target_group_display TEXT NOT NULL,
    phone TEXT,
    address_line TEXT,
    commune_code TEXT,
    district_code TEXT,
    province_code TEXT,
    managing_station_id TEXT,
    deceased_flag INTEGER NOT NULL DEFAULT 0 CHECK (deceased_flag IN (0, 1)),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    created_by TEXT NOT NULL,
    updated_by TEXT NOT NULL,
    raw_json TEXT
);

CREATE TABLE IF NOT EXISTS patient_identifiers (
    id TEXT PRIMARY KEY,
    patient_id TEXT NOT NULL,
    identifier_type TEXT NOT NULL,
    system_uri TEXT,
    value TEXT NOT NULL,
    is_primary INTEGER NOT NULL DEFAULT 0 CHECK (is_primary IN (0, 1)),
    verified_flag INTEGER NOT NULL DEFAULT 0 CHECK (verified_flag IN (0, 1)),
    issued_by TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
    UNIQUE (identifier_type, value)
);

CREATE TABLE IF NOT EXISTS questionnaires (
    id TEXT PRIMARY KEY,
    package_id TEXT NOT NULL,
    version TEXT NOT NULL,
    title TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('draft', 'active', 'retired')),
    source_uri TEXT,
    definition_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE (package_id, version)
);

CREATE TABLE IF NOT EXISTS encounters (
    id TEXT PRIMARY KEY,
    patient_id TEXT NOT NULL,
    encounter_class TEXT NOT NULL CHECK (encounter_class IN ('ambulatory', 'community', 'field', 'other')),
    encounter_type_code TEXT NOT NULL,
    encounter_type_display TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('planned', 'in-progress', 'finished', 'cancelled', 'entered-in-error')),
    service_provider TEXT,
    station_id TEXT NOT NULL,
    commune_code TEXT,
    location_name TEXT,
    start_at TEXT NOT NULL,
    end_at TEXT,
    encounter_date TEXT NOT NULL,
    author TEXT NOT NULL,
    source_mode TEXT NOT NULL CHECK (source_mode IN ('manual', 'omr', 'import', 'sync', 'migration')),
    package_id TEXT NOT NULL,
    questionnaire_id TEXT,
    summary_text TEXT,
    classification_code TEXT,
    classification_display TEXT,
    sync_state TEXT NOT NULL CHECK (sync_state IN ('local_only', 'committed', 'pushed', 'synced')),
    last_synced_at TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    raw_json TEXT,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
    FOREIGN KEY (questionnaire_id) REFERENCES questionnaires(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS encounter_participants (
    id TEXT PRIMARY KEY,
    encounter_id TEXT NOT NULL,
    role_code TEXT NOT NULL CHECK (role_code IN ('doctor', 'nurse', 'recorder', 'reviewer', 'other')),
    participant_name TEXT NOT NULL,
    participant_user TEXT,
    participant_license TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (encounter_id) REFERENCES encounters(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS observations (
    id TEXT PRIMARY KEY,
    patient_id TEXT NOT NULL,
    encounter_id TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('registered', 'preliminary', 'final', 'amended', 'entered-in-error')),
    category_code TEXT NOT NULL,
    category_display TEXT NOT NULL,
    code TEXT NOT NULL,
    code_system TEXT NOT NULL,
    code_display TEXT NOT NULL,
    value_type TEXT NOT NULL CHECK (value_type IN ('quantity', 'text', 'coded', 'boolean', 'integer', 'component', 'ratio')),
    value_number REAL,
    value_text TEXT,
    value_code TEXT,
    value_code_system TEXT,
    value_display TEXT,
    unit TEXT,
    reference_low REAL,
    reference_high REAL,
    interpretation_code TEXT,
    interpretation_display TEXT,
    body_site_code TEXT,
    method_code TEXT,
    effective_at TEXT NOT NULL,
    issued_at TEXT,
    performer_name TEXT,
    source_section_id TEXT,
    source_field_id TEXT,
    derived_from_observation_id TEXT,
    panel_code TEXT,
    note_text TEXT,
    raw_json TEXT,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
    FOREIGN KEY (encounter_id) REFERENCES encounters(id) ON DELETE CASCADE,
    FOREIGN KEY (derived_from_observation_id) REFERENCES observations(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS conditions (
    id TEXT PRIMARY KEY,
    patient_id TEXT NOT NULL,
    encounter_id TEXT,
    clinical_status TEXT NOT NULL CHECK (clinical_status IN ('active', 'recurrence', 'inactive', 'resolved', 'remission', 'unknown')),
    verification_status TEXT NOT NULL CHECK (verification_status IN ('unconfirmed', 'provisional', 'confirmed', 'differential', 'refuted', 'entered-in-error')),
    category_code TEXT NOT NULL,
    code TEXT,
    code_system TEXT,
    code_display TEXT NOT NULL,
    body_site_code TEXT,
    severity_code TEXT,
    onset_date TEXT,
    abatement_date TEXT,
    recorded_at TEXT NOT NULL,
    asserter_name TEXT,
    source_section_id TEXT,
    source_field_id TEXT,
    note_text TEXT,
    raw_json TEXT,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
    FOREIGN KEY (encounter_id) REFERENCES encounters(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS questionnaire_responses (
    id TEXT PRIMARY KEY,
    patient_id TEXT NOT NULL,
    encounter_id TEXT NOT NULL,
    questionnaire_id TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('in-progress', 'completed', 'amended', 'entered-in-error', 'stopped')),
    authored_at TEXT NOT NULL,
    author_name TEXT NOT NULL,
    package_id TEXT NOT NULL,
    response_json TEXT NOT NULL,
    source_record_json TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
    FOREIGN KEY (encounter_id) REFERENCES encounters(id) ON DELETE CASCADE,
    FOREIGN KEY (questionnaire_id) REFERENCES questionnaires(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS audit_events (
    id TEXT PRIMARY KEY,
    entity_type TEXT NOT NULL CHECK (entity_type IN ('patient', 'encounter', 'observation', 'condition', 'questionnaire_response', 'sync')),
    entity_id TEXT,
    action TEXT NOT NULL CHECK (action IN ('create', 'update', 'delete', 'sync', 'migrate', 'import')),
    actor TEXT NOT NULL,
    station_id TEXT,
    occurred_at TEXT NOT NULL,
    details_json TEXT
);

CREATE TABLE IF NOT EXISTS code_map_local (
    id TEXT PRIMARY KEY,
    domain_name TEXT NOT NULL,
    source_section_id TEXT,
    source_field_id TEXT,
    local_code TEXT NOT NULL,
    local_display TEXT NOT NULL,
    standard_code TEXT,
    standard_system TEXT,
    standard_display TEXT,
    active INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0, 1)),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE (domain_name, local_code)
);

CREATE TABLE IF NOT EXISTS attachments (
    id TEXT PRIMARY KEY,
    patient_id TEXT,
    encounter_id TEXT,
    attachment_type TEXT NOT NULL,
    mime_type TEXT,
    file_path TEXT NOT NULL,
    file_hash TEXT,
    captured_at TEXT,
    created_at TEXT NOT NULL,
    created_by TEXT NOT NULL,
    metadata_json TEXT,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE SET NULL,
    FOREIGN KEY (encounter_id) REFERENCES encounters(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_patients_full_name
    ON patients(full_name);

CREATE INDEX IF NOT EXISTS idx_patients_birth_date
    ON patients(birth_date);

CREATE INDEX IF NOT EXISTS idx_patients_target_group_code
    ON patients(target_group_code);

CREATE INDEX IF NOT EXISTS idx_patients_managing_station_id
    ON patients(managing_station_id);

CREATE INDEX IF NOT EXISTS idx_patient_identifiers_patient_id
    ON patient_identifiers(patient_id);

CREATE INDEX IF NOT EXISTS idx_patient_identifiers_value
    ON patient_identifiers(value);

CREATE INDEX IF NOT EXISTS idx_questionnaires_package_id
    ON questionnaires(package_id);

CREATE INDEX IF NOT EXISTS idx_encounters_patient_date
    ON encounters(patient_id, encounter_date);

CREATE INDEX IF NOT EXISTS idx_encounters_station_date
    ON encounters(station_id, encounter_date);

CREATE INDEX IF NOT EXISTS idx_encounters_package_id
    ON encounters(package_id);

CREATE INDEX IF NOT EXISTS idx_encounters_sync_state
    ON encounters(sync_state);

CREATE INDEX IF NOT EXISTS idx_encounter_participants_encounter_id
    ON encounter_participants(encounter_id);

CREATE INDEX IF NOT EXISTS idx_observations_patient_id
    ON observations(patient_id);

CREATE INDEX IF NOT EXISTS idx_observations_encounter_id
    ON observations(encounter_id);

CREATE INDEX IF NOT EXISTS idx_observations_code
    ON observations(code);

CREATE INDEX IF NOT EXISTS idx_observations_source_field
    ON observations(source_section_id, source_field_id);

CREATE INDEX IF NOT EXISTS idx_observations_effective_at
    ON observations(effective_at);

CREATE INDEX IF NOT EXISTS idx_conditions_patient_id
    ON conditions(patient_id);

CREATE INDEX IF NOT EXISTS idx_conditions_encounter_id
    ON conditions(encounter_id);

CREATE INDEX IF NOT EXISTS idx_conditions_code
    ON conditions(code);

CREATE INDEX IF NOT EXISTS idx_conditions_clinical_status
    ON conditions(clinical_status);

CREATE INDEX IF NOT EXISTS idx_questionnaire_responses_patient_id
    ON questionnaire_responses(patient_id);

CREATE INDEX IF NOT EXISTS idx_questionnaire_responses_encounter_id
    ON questionnaire_responses(encounter_id);

CREATE INDEX IF NOT EXISTS idx_questionnaire_responses_package_id
    ON questionnaire_responses(package_id);

CREATE INDEX IF NOT EXISTS idx_audit_events_entity
    ON audit_events(entity_type, entity_id);

CREATE INDEX IF NOT EXISTS idx_audit_events_occurred_at
    ON audit_events(occurred_at);

CREATE INDEX IF NOT EXISTS idx_code_map_local_domain_field
    ON code_map_local(domain_name, source_section_id, source_field_id);

CREATE INDEX IF NOT EXISTS idx_attachments_patient_id
    ON attachments(patient_id);

CREATE INDEX IF NOT EXISTS idx_attachments_encounter_id
    ON attachments(encounter_id);
