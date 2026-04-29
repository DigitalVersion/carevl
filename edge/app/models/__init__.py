from app.models.patient import Patient
from app.models.patient_identifier import PatientIdentifier
from app.models.encounter import Encounter
from app.models.encounter_participant import EncounterParticipant
from app.models.observation import Observation
from app.models.condition import Condition
from app.models.questionnaire import Questionnaire
from app.models.questionnaire_response import QuestionnaireResponse
from app.models.diagnostic_report import DiagnosticReport
from app.models.measure_report import MeasureReport
from app.models.audit_event import AuditEvent
from app.models.code_map_local import CodeMapLocal
from app.models.attachment import Attachment
from app.models.system_config import SystemConfig

# This ensures all models are imported and registered with the Base
# so that Base.metadata.create_all() creates all tables.

__all__ = [
    "Patient",
    "PatientIdentifier",
    "Encounter",
    "EncounterParticipant",
    "Observation",
    "Condition",
    "Questionnaire",
    "QuestionnaireResponse",
    "DiagnosticReport",
    "MeasureReport",
    "AuditEvent",
    "CodeMapLocal",
    "Attachment",
    "SystemConfig",
]
