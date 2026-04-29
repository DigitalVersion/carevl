from sqlalchemy import Column, String, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base


class Condition(Base):
    """
    FHIR Condition resource
    Store medical history, diagnosis, conclusions
    """
    __tablename__ = "conditions"

    # Primary key: UUID v4
    id = Column(String, primary_key=True, index=True)
    
    # Foreign keys
    patient_id = Column(String, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    encounter_id = Column(String, ForeignKey("encounters.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Condition code (ICD-10, SNOMED, local)
    code_system = Column(String, nullable=False, default="local")
    code = Column(String, nullable=False, index=True)
    code_display = Column(String, nullable=False)
    
    # Category: 'problem-list-item', 'encounter-diagnosis', 'medical-history'
    category = Column(String, nullable=True, index=True)
    
    # Clinical status: 'active', 'resolved', 'inactive', 'remission'
    clinical_status = Column(String, nullable=True, default="active", index=True)
    
    # Verification status: 'confirmed', 'provisional', 'differential', 'refuted'
    verification_status = Column(String, nullable=True, default="confirmed")
    
    # Severity: 'mild', 'moderate', 'severe'
    severity = Column(String, nullable=True)
    
    # Onset
    onset_datetime = Column(DateTime, nullable=True)
    onset_string = Column(String, nullable=True)
    
    # Abatement (resolution)
    abatement_datetime = Column(DateTime, nullable=True)
    abatement_string = Column(String, nullable=True)
    
    # Note
    note = Column(String, nullable=True)
    
    # Metadata
    recorded_date = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    recorder = Column(String, nullable=True)
    station_id = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Soft delete
    deleted_at = Column(DateTime, nullable=True)
    
    # Relationships
    patient = relationship("Patient", back_populates="conditions")
    encounter = relationship("Encounter", back_populates="conditions")
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "clinical_status IN ('active', 'resolved', 'inactive', 'remission')",
            name="check_clinical_status"
        ),
        CheckConstraint(
            "verification_status IN ('confirmed', 'provisional', 'differential', 'refuted')",
            name="check_verification_status"
        ),
        CheckConstraint(
            "severity IN ('mild', 'moderate', 'severe')",
            name="check_severity"
        ),
    )
