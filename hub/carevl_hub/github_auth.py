"""
GitHub Device Flow Authentication for Hub Admin.

Allows Hub Admin to authenticate with GitHub to automatically create
repos and PATs for stations.
"""

from __future__ import annotations

import time
from typing import Optional

import requests
from pydantic import BaseModel


# CareVL Hub OAuth App - set via GUI (Tab 1 → Client ID field)
# Register at: https://github.com/settings/developers → New OAuth App
GITHUB_CLIENT_ID = ""  # Not used directly — passed as parameter from GUI


class DeviceCodeResponse(BaseModel):
    """Response from GitHub device code endpoint"""
    device_code: str
    user_code: str
    verification_uri: str
    expires_in: int
    interval: int


class AccessTokenResponse(BaseModel):
    """Response from GitHub access token endpoint"""
    access_token: str
    token_type: str
    scope: str


class GitHubDeviceFlow:
    """Handle GitHub Device Flow authentication"""
    
    @staticmethod
    def start_device_flow(scope: str = "repo", client_id: str = GITHUB_CLIENT_ID) -> DeviceCodeResponse:
        """
        Start device flow authentication.
        
        Args:
            scope: GitHub OAuth scope (default: "repo")
            client_id: GitHub OAuth App Client ID
        
        Returns:
            DeviceCodeResponse with user_code and verification_uri
        
        Raises:
            requests.HTTPError: If GitHub API request fails
            ValueError: If client_id is empty
        """
        if not client_id:
            raise ValueError("Client ID is required. Enter it in the GUI (Tab 1 → Client ID field).")
        
        response = requests.post(
            "https://github.com/login/device/code",
            headers={
                "Accept": "application/json",
            },
            json={
                "client_id": client_id,
                "scope": scope,
            },
            timeout=10,
        )
        response.raise_for_status()
        
        data = response.json()
        return DeviceCodeResponse(**data)
    
    @staticmethod
    def poll_for_token(
        device_code: str,
        interval: int = 5,
        max_attempts: int = 60,
        client_id: str = GITHUB_CLIENT_ID,
    ) -> Optional[str]:
        """
        Poll GitHub for access token.
        
        Args:
            device_code: Device code from start_device_flow
            interval: Polling interval in seconds
            max_attempts: Maximum number of polling attempts
            client_id: GitHub OAuth App Client ID
        
        Returns:
            Access token if successful, None if timeout or user denied
        
        Raises:
            requests.HTTPError: If GitHub API request fails
        """
        for _ in range(max_attempts):
            time.sleep(interval)
            
            response = requests.post(
                "https://github.com/login/oauth/access_token",
                headers={
                    "Accept": "application/json",
                },
                json={
                    "client_id": client_id,
                    "device_code": device_code,
                    "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                },
                timeout=10,
            )
            
            data = response.json()
            
            # Check response
            if "access_token" in data:
                token_response = AccessTokenResponse(**data)
                return token_response.access_token
            
            error = data.get("error")
            
            if error == "authorization_pending":
                continue
            elif error == "slow_down":
                time.sleep(interval)
                continue
            elif error in ("expired_token", "access_denied"):
                return None
            else:
                response.raise_for_status()
        
        return None
    
    @staticmethod
    def verify_token(token: str) -> bool:
        """
        Verify that token is valid.
        
        Args:
            token: GitHub access token
        
        Returns:
            True if token is valid, False otherwise
        """
        try:
            response = requests.get(
                "https://api.github.com/user",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28",
                },
                timeout=10,
            )
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    @staticmethod
    def get_user_info(token: str) -> dict:
        """
        Get authenticated user info.
        
        Args:
            token: GitHub access token
        
        Returns:
            User info dict with login, name, etc.
        
        Raises:
            requests.HTTPError: If GitHub API request fails
        """
        response = requests.get(
            "https://api.github.com/user",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
