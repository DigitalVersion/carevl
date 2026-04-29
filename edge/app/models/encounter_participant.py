from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base


class EncounterParticipant(Base):
    """
    FHIR Encounter.participant
    Store doctor, nurse, data_entry, reviewer, admin
    """
    __tablename__ = "encounter_participants"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign key
    encounter_id = Column(String, ForeignKey("encounters.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Participant details
    participant_type = Column(
        String, 
        nullable=False, 
        index=True
    )
    participant_name = Column(String, nullable=False)
    participant_id = Column(String, nullable=True)
    
    # Period
    period_start = Column(DateTime, nullable=True)
    period_end = Column(DateTime, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationship
    encounter = relationship("Encounter", back_populates="participants")
    
    # Constraint
    __table_args__ = (
        CheckConstraint(
            "participant_type IN ('doctor', 'nurse', 'data_entry', 'reviewer', 'admin')",
            name="check_participant_type"
        ),
    )
