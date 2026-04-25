from fastapi import APIRouter, HTTPException
import os
from datetime import datetime
from app.services.crypto import encrypt_file
from app.core.config import settings

router = APIRouter()

@router.post("/sync/snapshot/create")
def create_snapshot():
    """
    Creates an encrypted snapshot of the current local SQLite database.
    This is triggered by the Site Operator to lock data and prepare for sync.
    """
    db_path = settings.DATABASE_URL.replace("sqlite:///", "")

    if not os.path.exists(db_path):
        raise HTTPException(status_code=404, detail="Local database not found.")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    snapshot_filename = f"carevl_snapshot_{settings.SITE_ID}_{timestamp}.db.enc"
    snapshot_path = os.path.join(os.path.dirname(db_path), snapshot_filename)

    import sqlite3
    import tempfile

    try:
        # Create a temporary file to hold the safe database backup
        fd, temp_db_path = tempfile.mkstemp(suffix=".db")
        os.close(fd)

        # Connect to original DB and backup to temp DB safely handling WAL
        source = sqlite3.connect(db_path)
        dest = sqlite3.connect(temp_db_path)

        with source, dest:
            source.backup(dest)

        source.close()
        dest.close()

        # Encrypt the cleanly backed-up database
        encrypt_file(temp_db_path, snapshot_path)

        # Clean up temp file
        os.remove(temp_db_path)

        return {
            "status": "success",
            "message": "Snapshot created and encrypted successfully.",
            "snapshot_file": snapshot_filename
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to encrypt database: {str(e)}")
