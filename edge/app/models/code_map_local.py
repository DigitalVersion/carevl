from sqlalchemy import Column, Integer, String, DateTime, CheckConstraint, UniqueConstraint
from datetime import datetime, timezone
from app.core.database import Base


class CodeMapLocal(Base):
    """
    Map local codes to standard terminologies (LOINC, SNOMED, ICD-10)
    """
    __tablename__ = "code_map_local"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Local code
    local_code = Column(String, nullable=False, index=True)
    local_display = Column(String, nullable=False)
    local_system = Column(String, nullable=False, default="local")
    
    # Target code
    target_system = Column(String, nullable=True)
    target_code = Column(String, nullable=True, index=True)
    target_display = Column(String, nullable=True)
    
    # Mapping details
    equivalence = Column(String, nullable=False, default="equivalent")
    comment = Column(String, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "target_system IN ('loinc', 'snomed', 'icd10', 'rxnorm')",
            name="check_target_system"
        ),
        CheckConstraint(
            "equivalence IN ('equivalent', 'wider', 'narrower', 'inexact', 'unmatched')",
            name="check_equivalence"
        ),
        UniqueConstraint("local_code", "target_system", name="uq_code_map_local_target"),
    )
