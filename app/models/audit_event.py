from sqlalchemy import Column, Integer, String, DateTime, CheckConstraint
from datetime import datetime, timezone
from app.core.database import Base


class AuditEvent(Base):
    """
    FHIR AuditEvent resource
    Track create/update/delete/migrate/sync operations
    """
    __tablename__ = "audit_events"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Event details
    event_type = Column(String, nullable=False, index=True)
    event_action = Column(String, nullable=True)
    event_outcome = Column(String, nullable=True)
    
    # Resource reference
    resource_type = Column(String, nullable=True, index=True)
    resource_id = Column(String, nullable=True, index=True)
    
    # Agent (who did it)
    agent_type = Column(String, nullable=True)
    agent_name = Column(String, nullable=True)
    agent_id = Column(String, nullable=True, index=True)
    
    # Source (where it happened)
    source_station_id = Column(String, nullable=True)
    source_ip = Column(String, nullable=True)
    
    # Details
    description = Column(String, nullable=True)
    changes_json = Column(String, nullable=True)
    
    # Timestamp
    recorded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "event_type IN ('create', 'update', 'delete', 'migrate', 'sync', 'export', 'import', 'login', 'logout')",
            name="check_event_type"
        ),
        CheckConstraint(
            "event_outcome IN ('success', 'failure', 'warning')",
            name="check_event_outcome"
        ),
        CheckConstraint(
            "agent_type IN ('user', 'system', 'device')",
            name="check_agent_type"
        ),
    )
