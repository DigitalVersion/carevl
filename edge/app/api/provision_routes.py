"""Provisioning routes for invite code authentication"""

from fastapi import APIRouter, HTTPException, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

from edge.app.services.invite_code import InviteCodeService
from edge.app.services.credential_manager import CredentialManager
from edge.app.services.git_operations import GitOperations
from edge.app.core.config import settings

router = APIRouter(prefix="/provision", tags=["provision"])
templates = Jinja2Templates(directory="edge/app/templates")


@router.get("/", response_class=HTMLResponse)
async def provision_page(request: Request):
    """Show provisioning page"""
    return templates.TemplateResponse(
        "provision/index.html",
        {"request": request}
    )


@router.post("/validate-code")
async def validate_invite_code(invite_code: str = Form(...)):
    """
    Validate invite code
    
    Returns:
        JSON with validation result and parsed data
    """
    is_valid, error = InviteCodeService.validate(invite_code)
    
    if not is_valid:
        raise HTTPException(status_code=400, detail=error)
    
    # Decode and return data
    data = InviteCodeService.decode(invite_code)
    
    return {
        "status": "success",
        "data": {
            "station_id": data.station_id,
            "station_name": data.station_name,
            "repo_url": data.repo_url,
            "has_encryption_key": data.encryption_key is not None
        }
    }


@router.post("/setup-new")
async def setup_new_station(
    invite_code: str = Form(...),
    pin: str = Form(..., min_length=6, max_length=6)
):
    """
    Setup new station with invite code
    
    Steps:
    1. Decode invite code
    2. Save PAT to Credential Manager
    3. Save encryption key (if provided)
    4. Clone repository
    5. Initialize database
    6. Save PIN
    7. Redirect to dashboard
    """
    try:
        # 1. Decode invite code
        data = InviteCodeService.decode(invite_code)
        
        # 2. Check if Git is installed
        if not GitOperations.check_git_installed():
            raise HTTPException(
                status_code=500,
                detail="Git is not installed. Please install Git first."
            )
        
        # 3. Save PAT to Credential Manager
        if not CredentialManager.save_pat(data.station_id, data.pat):
            raise HTTPException(
                status_code=500,
                detail="Failed to save PAT to Credential Manager"
            )
        
        # 4. Save encryption key (if provided)
        if data.encryption_key:
            if not CredentialManager.save_encryption_key(data.station_id, data.encryption_key):
                raise HTTPException(
                    status_code=500,
                    detail="Failed to save encryption key"
                )
        
        # 5. Clone repository
        repo_dir = Path(f"./data/repos/{data.station_id}")
        success, message = GitOperations.clone_repo(data.repo_url, data.pat, repo_dir)
        
        if not success:
            raise HTTPException(status_code=500, detail=message)
        
        # 6. Initialize database (create new empty database)
        # TODO: Initialize database with schema
        
        # 7. Save station config
        settings.STATION_ID = data.station_id
        settings.STATION_NAME = data.station_name
        settings.REPO_URL = data.repo_url
        
        # 8. Save PIN (TODO: implement PIN storage)
        
        return {
            "status": "success",
            "message": "Station setup completed successfully",
            "station_id": data.station_id,
            "station_name": data.station_name
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Setup failed: {e}")


@router.post("/setup-restore")
async def setup_restore_station(
    invite_code: str = Form(...),
    pin: str = Form(..., min_length=6, max_length=6)
):
    """
    Restore station from existing repository
    
    Steps:
    1. Decode invite code
    2. Save PAT to Credential Manager
    3. Clone repository
    4. Find latest snapshot
    5. Decrypt and restore database
    6. Save PIN
    7. Redirect to dashboard
    """
    try:
        # 1. Decode invite code
        data = InviteCodeService.decode(invite_code)
        
        # 2. Check if Git is installed
        if not GitOperations.check_git_installed():
            raise HTTPException(
                status_code=500,
                detail="Git is not installed. Please install Git first."
            )
        
        # 3. Save PAT to Credential Manager
        if not CredentialManager.save_pat(data.station_id, data.pat):
            raise HTTPException(
                status_code=500,
                detail="Failed to save PAT to Credential Manager"
            )
        
        # 4. Save encryption key (if provided)
        if data.encryption_key:
            if not CredentialManager.save_encryption_key(data.station_id, data.encryption_key):
                raise HTTPException(
                    status_code=500,
                    detail="Failed to save encryption key"
                )
        
        # 5. Clone repository
        repo_dir = Path(f"./data/repos/{data.station_id}")
        success, message = GitOperations.clone_repo(data.repo_url, data.pat, repo_dir)
        
        if not success:
            raise HTTPException(status_code=500, detail=message)
        
        # 6. Find latest snapshot in releases
        # TODO: Implement snapshot discovery and restore
        
        # 7. Decrypt and restore database
        # TODO: Implement database restore
        
        # 8. Save station config
        settings.STATION_ID = data.station_id
        settings.STATION_NAME = data.station_name
        settings.REPO_URL = data.repo_url
        
        # 9. Save PIN (TODO: implement PIN storage)
        
        return {
            "status": "success",
            "message": "Station restored successfully",
            "station_id": data.station_id,
            "station_name": data.station_name
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Restore failed: {e}")


@router.get("/status")
async def provision_status():
    """
    Check if station is provisioned
    
    Returns:
        JSON with provisioning status
    """
    station_id = getattr(settings, 'STATION_ID', None)
    
    if not station_id:
        return {
            "provisioned": False,
            "message": "Station not provisioned"
        }
    
    # Check if PAT exists
    pat = CredentialManager.get_pat(station_id)
    
    return {
        "provisioned": pat is not None,
        "station_id": station_id,
        "station_name": getattr(settings, 'STATION_NAME', None)
    }
