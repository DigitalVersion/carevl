"""Shared Pydantic models for CareVL Edge and Hub"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class SnapshotMetadata(BaseModel):
    """Metadata for encrypted snapshot"""
    station_id: str
    timestamp: datetime
    file_name: str
    file_size: Optional[int] = None
    checksum: Optional[str] = None


class InviteCode(BaseModel):
    """Invite code structure for station provisioning"""
    station_id: str
    station_name: str
    repo_url: str
    pat: str  # GitHub Personal Access Token
    encryption_key: Optional[str] = None


class SyncStatus(BaseModel):
    """Sync status for a station"""
    station_id: str
    last_sync: Optional[datetime] = None
    sync_state: str  # 'pending', 'synced', 'error'
    error_message: Optional[str] = None
    snapshot_count: int = 0


class PatientIdentifierData(BaseModel):
    """Patient identifier data"""
    system: str  # 'CCCD', 'VNeID', 'BHYT', 'MRN'
    value: str
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None


class ObservationValue(BaseModel):
    """Polymorphic observation value"""
    value_type: str  # 'string', 'numeric', 'boolean', 'datetime', 'codeable'
    value_string: Optional[str] = None
    value_numeric: Optional[float] = None
    value_boolean: Optional[bool] = None
    value_datetime: Optional[datetime] = None
    value_code: Optional[str] = None
    value_code_display: Optional[str] = None
    unit: Optional[str] = None


class CodeMapping(BaseModel):
    """Code mapping from local to standard terminology"""
    local_code: str
    local_display: str
    local_system: str = "local"
    target_system: Optional[str] = None  # 'loinc', 'snomed', 'icd10'
    target_code: Optional[str] = None
    target_display: Optional[str] = None
    equivalence: str = "equivalent"


class AuditEventData(BaseModel):
    """Audit event data"""
    event_type: str  # 'create', 'update', 'delete', 'migrate', 'sync'
    event_outcome: str  # 'success', 'failure', 'warning'
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    agent_type: Optional[str] = None
    agent_name: Optional[str] = None
    description: Optional[str] = None
    changes: Optional[Dict[str, Any]] = None


class DataQualityIssue(BaseModel):
    """Data quality issue"""
    severity: str  # 'error', 'warning', 'info'
    category: str  # 'missing', 'invalid', 'duplicate', 'outlier'
    resource_type: str
    resource_id: str
    field_name: Optional[str] = None
    message: str
    suggestion: Optional[str] = None


class HubReportSummary(BaseModel):
    """Hub aggregation report summary"""
    total_stations: int
    total_patients: int
    total_encounters: int
    total_observations: int
    date_range_start: datetime
    date_range_end: datetime
    generated_at: datetime
    quality_issues: int = 0
