from sqlalchemy import Column, String, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base


class QuestionnaireResponse(Base):
    """
    FHIR QuestionnaireResponse resource
    Store complete form responses
    """
    __tablename__ = "questionnaire_responses"

    # Primary key: UUID v4
    id = Column(String, primary_key=True, index=True)
    
    # Foreign keys
    questionnaire_id = Column(String, ForeignKey("questionnaires.id", ondelete="RESTRICT"), nullable=False, index=True)
    encounter_id = Column(String, ForeignKey("encounters.id", ondelete="CASCADE"), nullable=False, index=True)
    patient_id = Column(String, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Response status: 'in-progress', 'completed', 'amended'
    status = Column(String, nullable=False, default="in-progress", index=True)
    
    # Full response (JSON)
    response_json = Column(String, nullable=False)
    
    # Metadata
    authored_datetime = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    author = Column(String, nullable=True)
    station_id = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Soft delete
    deleted_at = Column(DateTime, nullable=True)
    
    # Relationships
    questionnaire = relationship("Questionnaire", back_populates="responses")
    encounter = relationship("Encounter", back_populates="questionnaire_responses")
    patient = relationship("Patient", back_populates="questionnaire_responses")
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "status IN ('in-progress', 'completed', 'amended')",
            name="check_status"
        ),
    )
