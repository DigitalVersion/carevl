from sqlalchemy import Column, String, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base


class Encounter(Base):
    """
    FHIR Encounter resource
    Each row is one visit/encounter
    """
    __tablename__ = "encounters"

    # Primary key: UUID v4
    id = Column(String, primary_key=True, index=True)
    
    # Foreign key
    patient_id = Column(String, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Business identifier
    sticker_id = Column(String, unique=True, nullable=True)
    
    # Encounter details
    encounter_date = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    encounter_class = Column(String, nullable=True, default="ambulatory")
    encounter_status = Column(String, nullable=True, default="arrived")
    
    # Package/program
    package_id = Column(String, nullable=True)
    package_name = Column(String, nullable=True)
    
    # Location
    station_id = Column(String, nullable=False, index=True)
    commune_code = Column(String, nullable=True)
    
    # Summary
    summary_text = Column(String, nullable=True)
    classification_display = Column(String, nullable=True)
    
    # Sync state
    sync_state = Column(String, nullable=True, default="pending", index=True)
    synced_at = Column(DateTime, nullable=True)
    
    # Metadata
    author = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Soft delete
    deleted_at = Column(DateTime, nullable=True)
    
    # Raw data for migration/audit
    raw_json = Column(String, nullable=True)
    
    # Relationships
    patient = relationship("Patient", back_populates="encounters")
    participants = relationship("EncounterParticipant", back_populates="encounter", cascade="all, delete-orphan")
    observations = relationship("Observation", back_populates="encounter", cascade="all, delete-orphan")
    conditions = relationship("Condition", back_populates="encounter")
    questionnaire_responses = relationship("QuestionnaireResponse", back_populates="encounter", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "encounter_class IN ('ambulatory', 'emergency', 'inpatient', 'outpatient', 'home')",
            name="check_encounter_class"
        ),
        CheckConstraint(
            "encounter_status IN ('planned', 'arrived', 'in-progress', 'finished', 'cancelled')",
            name="check_encounter_status"
        ),
        CheckConstraint(
            "sync_state IN ('pending', 'synced', 'error')",
            name="check_sync_state"
        ),
    )
