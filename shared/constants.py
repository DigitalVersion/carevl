"""Shared constants for CareVL Edge and Hub"""

# Encryption
ENCRYPTION_ALGORITHM = "AES-256-CBC"
ENCRYPTION_KEY_LENGTH = 32  # 256 bits

# File naming
SNAPSHOT_FILE_PATTERN = "FINAL_{station_id}_{timestamp}.db.enc"
SNAPSHOT_TIMESTAMP_FORMAT = "%Y-%m-%dT%H-%M-%S"

# Database
DB_JOURNAL_MODE = "WAL"
DB_SYNCHRONOUS = "NORMAL"

# Sync states
SYNC_STATE_PENDING = "pending"
SYNC_STATE_SYNCED = "synced"
SYNC_STATE_ERROR = "error"

# Encounter statuses
ENCOUNTER_STATUS_PLANNED = "planned"
ENCOUNTER_STATUS_ARRIVED = "arrived"
ENCOUNTER_STATUS_IN_PROGRESS = "in-progress"
ENCOUNTER_STATUS_FINISHED = "finished"
ENCOUNTER_STATUS_CANCELLED = "cancelled"

# Encounter classes
ENCOUNTER_CLASS_AMBULATORY = "ambulatory"
ENCOUNTER_CLASS_EMERGENCY = "emergency"
ENCOUNTER_CLASS_INPATIENT = "inpatient"
ENCOUNTER_CLASS_OUTPATIENT = "outpatient"
ENCOUNTER_CLASS_HOME = "home"

# Gender codes
GENDER_MALE = "male"
GENDER_FEMALE = "female"
GENDER_OTHER = "other"
GENDER_UNKNOWN = "unknown"

# Identifier systems
IDENTIFIER_SYSTEM_CCCD = "CCCD"
IDENTIFIER_SYSTEM_VNEID = "VNeID"
IDENTIFIER_SYSTEM_BHYT = "BHYT"
IDENTIFIER_SYSTEM_MRN = "MRN"
IDENTIFIER_SYSTEM_PASSPORT = "passport"

# Observation categories
OBS_CATEGORY_VITAL_SIGNS = "vital-signs"
OBS_CATEGORY_LABORATORY = "laboratory"
OBS_CATEGORY_IMAGING = "imaging"
OBS_CATEGORY_EXAM = "exam"

# Condition categories
CONDITION_CATEGORY_PROBLEM = "problem-list-item"
CONDITION_CATEGORY_DIAGNOSIS = "encounter-diagnosis"
CONDITION_CATEGORY_HISTORY = "medical-history"

# Clinical statuses
CLINICAL_STATUS_ACTIVE = "active"
CLINICAL_STATUS_RESOLVED = "resolved"
CLINICAL_STATUS_INACTIVE = "inactive"
CLINICAL_STATUS_REMISSION = "remission"

# Verification statuses
VERIFICATION_STATUS_CONFIRMED = "confirmed"
VERIFICATION_STATUS_PROVISIONAL = "provisional"
VERIFICATION_STATUS_DIFFERENTIAL = "differential"
VERIFICATION_STATUS_REFUTED = "refuted"

# Audit event types
AUDIT_EVENT_CREATE = "create"
AUDIT_EVENT_UPDATE = "update"
AUDIT_EVENT_DELETE = "delete"
AUDIT_EVENT_MIGRATE = "migrate"
AUDIT_EVENT_SYNC = "sync"
AUDIT_EVENT_EXPORT = "export"
AUDIT_EVENT_IMPORT = "import"
AUDIT_EVENT_LOGIN = "login"
AUDIT_EVENT_LOGOUT = "logout"

# Audit outcomes
AUDIT_OUTCOME_SUCCESS = "success"
AUDIT_OUTCOME_FAILURE = "failure"
AUDIT_OUTCOME_WARNING = "warning"

# Agent types
AGENT_TYPE_USER = "user"
AGENT_TYPE_SYSTEM = "system"
AGENT_TYPE_DEVICE = "device"

# Participant types
PARTICIPANT_TYPE_DOCTOR = "doctor"
PARTICIPANT_TYPE_NURSE = "nurse"
PARTICIPANT_TYPE_DATA_ENTRY = "data_entry"
PARTICIPANT_TYPE_REVIEWER = "reviewer"
PARTICIPANT_TYPE_ADMIN = "admin"

# Questionnaire statuses
QUESTIONNAIRE_STATUS_DRAFT = "draft"
QUESTIONNAIRE_STATUS_ACTIVE = "active"
QUESTIONNAIRE_STATUS_RETIRED = "retired"

# Response statuses
RESPONSE_STATUS_IN_PROGRESS = "in-progress"
RESPONSE_STATUS_COMPLETED = "completed"
RESPONSE_STATUS_AMENDED = "amended"

# Code systems
CODE_SYSTEM_LOCAL = "local"
CODE_SYSTEM_LOINC = "loinc"
CODE_SYSTEM_SNOMED = "snomed"
CODE_SYSTEM_ICD10 = "icd10"
CODE_SYSTEM_RXNORM = "rxnorm"

# Value types
VALUE_TYPE_STRING = "string"
VALUE_TYPE_NUMERIC = "numeric"
VALUE_TYPE_BOOLEAN = "boolean"
VALUE_TYPE_DATETIME = "datetime"
VALUE_TYPE_CODEABLE = "codeable"
