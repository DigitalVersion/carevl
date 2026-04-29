from sqlalchemy import Column, String, Date, DateTime, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base


class Patient(Base):
    """
    FHIR Patient resource
    Store basic patient demographics
    """
    __tablename__ = "patients"

    # Primary key: UUID v4
    id = Column(String, primary_key=True, index=True)
    
    # Demographics
    full_name = Column(String, nullable=False, index=True)
    birth_date = Column(Date, nullable=False, index=True)
    gender_code = Column(String, nullable=True)
    
    # Contact
    phone_number = Column(String, nullable=True)
    email = Column(String, nullable=True)
    address_line = Column(String, nullable=True)
    address_district = Column(String, nullable=True)
    address_province = Column(String, nullable=True)
    
    # Metadata
    station_id = Column(String, nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Soft delete
    deleted_at = Column(DateTime, nullable=True, index=True)
    
    # Raw data for migration/audit
    raw_json = Column(String, nullable=True)
    
    # Relationships
    identifiers = relationship("PatientIdentifier", back_populates="patient", cascade="all, delete-orphan")
    encounters = relationship("Encounter", back_populates="patient", cascade="all, delete-orphan")
    conditions = relationship("Condition", back_populates="patient", cascade="all, delete-orphan")
    questionnaire_responses = relationship("QuestionnaireResponse", back_populates="patient", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "gender_code IN ('male', 'female', 'other', 'unknown')",
            name="check_gender_code"
        ),
    )
