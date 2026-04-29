from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base


class PatientIdentifier(Base):
    """
    FHIR Patient.identifier
    Store CCCD, VNeID, BHYT, MRN, passport
    """
    __tablename__ = "patient_identifiers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign key
    patient_id = Column(String, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Identifier system: 'CCCD', 'VNeID', 'BHYT', 'MRN', 'passport'
    system = Column(String, nullable=False, index=True)
    
    # Identifier value
    value = Column(String, nullable=False, index=True)
    
    # Period of validity
    valid_from = Column(Date, nullable=True)
    valid_until = Column(Date, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationship
    patient = relationship("Patient", back_populates="identifiers")
