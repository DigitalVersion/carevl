from sqlalchemy import Column, String, DateTime, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base


class Questionnaire(Base):
    """
    FHIR Questionnaire resource
    Version control for template_form.json
    """
    __tablename__ = "questionnaires"

    # Primary key: UUID v4
    id = Column(String, primary_key=True, index=True)
    
    # Questionnaire details
    title = Column(String, nullable=False, index=True)
    version = Column(String, nullable=False, index=True)
    status = Column(String, nullable=False, default="active", index=True)
    
    # Full questionnaire definition (JSON)
    definition_json = Column(String, nullable=False)
    
    # Metadata
    station_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    responses = relationship("QuestionnaireResponse", back_populates="questionnaire")
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "status IN ('draft', 'active', 'retired')",
            name="check_status"
        ),
        UniqueConstraint("title", "version", name="uq_questionnaire_title_version"),
    )
