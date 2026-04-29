from sqlalchemy import Column, String, Integer, DateTime, Float, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base


class Observation(Base):
    """
    FHIR Observation resource
    Store vital signs, lab results, clinical measurements
    """
    __tablename__ = "observations"

    # Primary key: UUID v4
    id = Column(String, primary_key=True, index=True)
    
    # Foreign keys
    encounter_id = Column(String, ForeignKey("encounters.id", ondelete="CASCADE"), nullable=False, index=True)
    patient_id = Column(String, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Observation code (LOINC, SNOMED, local)
    code_system = Column(String, nullable=False, default="local")
    code = Column(String, nullable=False, index=True)
    code_display = Column(String, nullable=False)
    
    # Category: 'vital-signs', 'laboratory', 'imaging', 'exam'
    category = Column(String, nullable=True, index=True)
    
    # Value (polymorphic)
    value_type = Column(String, nullable=False)
    value_string = Column(String, nullable=True)
    value_numeric = Column(Float, nullable=True)
    value_boolean = Column(Integer, nullable=True)
    value_datetime = Column(DateTime, nullable=True)
    value_code = Column(String, nullable=True)
    value_code_display = Column(String, nullable=True)
    
    # Unit
    unit = Column(String, nullable=True)
    unit_system = Column(String, nullable=True)
    
    # Reference range
    reference_range_low = Column(Float, nullable=True)
    reference_range_high = Column(Float, nullable=True)
    reference_range_text = Column(String, nullable=True)
    
    # Interpretation: 'normal', 'abnormal', 'critical'
    interpretation = Column(String, nullable=True)
    
    # Source tracking (for migration from dynamic forms)
    source_section_id = Column(String, nullable=True, index=True)
    source_field_id = Column(String, nullable=True, index=True)
    
    # Metadata
    effective_datetime = Column(DateTime, nullable=True, index=True)
    issued_datetime = Column(DateTime, nullable=True)
    performer = Column(String, nullable=True)
    station_id = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Soft delete
    deleted_at = Column(DateTime, nullable=True)
    
    # Relationships
    encounter = relationship("Encounter", back_populates="observations")
    patient = relationship("Patient")
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "value_type IN ('string', 'numeric', 'boolean', 'datetime', 'codeable')",
            name="check_value_type"
        ),
        CheckConstraint(
            "value_boolean IN (0, 1)",
            name="check_value_boolean"
        ),
    )
