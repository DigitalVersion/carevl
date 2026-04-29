"""Configuration management for CareVL Hub"""

from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Optional


class HubSettings(BaseSettings):
    """Hub configuration settings"""
    
    # GitHub
    github_token: str
    github_org: str
    
    # Encryption
    encryption_key: str
    
    # Directories
    output_dir: Path = Path("./hub_data")
    snapshots_dir: Path = Path("./hub_data/snapshots")
    decrypted_dir: Path = Path("./hub_data/decrypted")
    reports_dir: Path = Path("./hub_data/reports")
    
    # DuckDB
    duckdb_path: Optional[Path] = None
    duckdb_memory_limit: str = "4GB"
    duckdb_threads: int = 4
    
    # Logging
    log_level: str = "INFO"
    log_file: Optional[Path] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def load_settings() -> HubSettings:
    """Load settings from .env file"""
    return HubSettings()
