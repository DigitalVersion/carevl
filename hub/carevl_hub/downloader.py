"""GitHub snapshot downloader for CareVL Hub"""

import httpx
from pathlib import Path
from typing import List, Optional
from datetime import datetime


class GitHubDownloader:
    """Download encrypted snapshots from GitHub Releases"""
    
    def __init__(self, token: str, org: str):
        self.token = token
        self.org = org
        self.headers = {"Authorization": f"Bearer {token}"}
        self.base_url = "https://api.github.com"
    
    def list_repos(self) -> List[str]:
        """List all repositories in organization"""
        url = f"{self.base_url}/orgs/{self.org}/repos"
        response = httpx.get(url, headers=self.headers)
        response.raise_for_status()
        repos = response.json()
        return [repo["name"] for repo in repos]
    
    def list_releases(self, repo: str) -> List[dict]:
        """List all releases for a repository"""
        url = f"{self.base_url}/repos/{self.org}/{repo}/releases"
        response = httpx.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def download_asset(self, asset_url: str, output_path: Path):
        """Download a release asset"""
        response = httpx.get(asset_url, headers=self.headers, follow_redirects=True)
        response.raise_for_status()
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(response.content)
    
    def download_snapshots(
        self,
        output_dir: Path,
        date: Optional[str] = None,
        repos: Optional[List[str]] = None,
        latest: bool = False
    ) -> List[Path]:
        """
        Download snapshots from GitHub Releases
        
        Args:
            output_dir: Directory to save snapshots
            date: Filter by date (YYYY-MM-DD)
            repos: List of specific repos to download
            latest: Download only latest snapshot per repo
        
        Returns:
            List of downloaded file paths
        """
        downloaded_files = []
        
        # Get list of repos
        if repos is None:
            repos = self.list_repos()
        
        for repo in repos:
            print(f"Processing repo: {repo}")
            
            try:
                releases = self.list_releases(repo)
                
                for release in releases:
                    # Filter by date if specified
                    if date:
                        release_date = datetime.fromisoformat(
                            release["published_at"].replace("Z", "+00:00")
                        ).date()
                        target_date = datetime.fromisoformat(date).date()
                        if release_date != target_date:
                            continue
                    
                    # Download assets
                    for asset in release.get("assets", []):
                        if asset["name"].endswith(".db.enc"):
                            output_path = output_dir / repo / asset["name"]
                            print(f"  Downloading: {asset['name']}")
                            self.download_asset(asset["browser_download_url"], output_path)
                            downloaded_files.append(output_path)
                            
                            if latest:
                                break  # Only download first (latest) asset
                    
                    if latest:
                        break  # Only process first (latest) release
            
            except Exception as e:
                print(f"  Error processing {repo}: {e}")
                continue
        
        return downloaded_files
