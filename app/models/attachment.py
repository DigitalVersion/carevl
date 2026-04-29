from sqlalchemy import Column, Integer, String, DateTime, CheckConstraint
from datetime import datetime, timezone
from app.core.database import Base


class Attachment(Base):
    """
    FHIR DocumentReference / Media
    Store file references (images, PDFs, etc.)
    """
    __tablename__ = "attachments"

    # Primary key: UUID v4
    id = Column(String, primary_key=True, index=True)
    
    # Foreign keys (polymorphic)
    resource_type = Column(String, nullable=False, index=True)
    resource_id = Column(String, nullable=False, index=True)
    
    # File details
    content_type = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    file_size = Column(Integer, nullable=True)
    file_path = Column(String, nullable=False)
    
    # Hash for integrity
    file_hash = Column(String, nullable=True)
    
    # Description
    title = Column(String, nullable=True)
    description = Column(String, nullable=True)
    
    # Metadata
    station_id = Column(String, nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    created_by = Column(String, nullable=True)
    
    # Soft delete
    deleted_at = Column(DateTime, nullable=True)
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "resource_type IN ('patient', 'encounter', 'observation', 'condition')",
            name="check_resource_type"
        ),
    )
