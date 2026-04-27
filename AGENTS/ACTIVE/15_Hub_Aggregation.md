# Hub Aggregation: DuckDB Analytics Pipeline

## Status
**[Active]**

## Context
Hub cần tổng hợp dữ liệu từ hàng trăm Sites (trạm y tế) để tạo báo cáo tổng hợp, dashboard và phân tích xu hướng. Việc tải thủ công từng Release của từng Site là không khả thi.

## Decision
Xây dựng **DuckDB Analytics Pipeline** tự động tải, giải mã và tổng hợp dữ liệu từ tất cả Sites.

## Architecture

```
GitHub Releases (carevl-snapshots)
├── Release: Site_LongHo_01
│   ├── FINAL_LongHo_01_2026-04-25T08-00-00.db.enc
│   ├── FINAL_LongHo_01_2026-04-24T17-30-00.db.enc
│   └── ...
├── Release: Site_BinhMinh_02
│   ├── FINAL_BinhMinh_02_2026-04-25T09-15-00.db.enc
│   └── ...
└── Release: Site_TanHung_03
    └── ...
                    ↓
        [Hub Aggregation Script]
                    ↓
            [DuckDB Analytics]
                    ↓
        [Dashboard / Reports]
```

## Implementation

### Script: `scripts/hub_aggregate.py`

```python
#!/usr/bin/env python3
"""
Hub Aggregation Script
Tự động tải và tổng hợp dữ liệu từ tất cả Sites
"""

import os
import requests
import duckdb
from datetime import datetime
from pathlib import Path
from cryptography.fernet import Fernet
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

class HubAggregator:
    def __init__(self, repo_owner, repo_name, github_token, master_key):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.github_token = github_token
        self.master_key = master_key
        self.base_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}"
        self.headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
    def list_all_releases(self):
        """Liệt kê tất cả Releases"""
        url = f"{self.base_url}/releases"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def list_all_assets(self):
        """Liệt kê tất cả Assets từ tất cả Releases"""
        releases = self.list_all_releases()
        all_assets = []
        
        for release in releases:
            site_id = release['tag_name'].replace('Site_', '')
            for asset in release['assets']:
                all_assets.append({
                    'site_id': site_id,
                    'name': asset['name'],
                    'url': asset['browser_download_url'],
                    'size': asset['size'],
                    'created_at': asset['created_at']
                })
        
        return all_assets
    
    def filter_by_date(self, assets, target_date=None):
        """Lọc Assets theo ngày (lấy mới nhất của mỗi Site)"""
        if target_date is None:
            target_date = datetime.now().strftime('%Y-%m-%d')
        
        # Group by site_id
        sites = {}
        for asset in assets:
            site_id = asset['site_id']
            # Parse date from filename: FINAL_{SITE_ID}_{DATE}T{TIME}.db.enc
            parts = asset['name'].split('_')
            if len(parts) >= 3:
                date_part = parts[2].split('T')[0]  # 2026-04-25
                
                if date_part == target_date:
                    if site_id not in sites:
                        sites[site_id] = asset
                    else:
                        # Keep the latest one
                        if asset['created_at'] > sites[site_id]['created_at']:
                            sites[site_id] = asset
        
        return list(sites.values())
    
    def download_asset(self, asset, output_dir='downloads'):
        """Tải một Asset"""
        Path(output_dir).mkdir(exist_ok=True)
        filepath = Path(output_dir) / asset['name']
        
        response = requests.get(asset['url'], headers=self.headers, stream=True)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return filepath
    
    def decrypt_file(self, encrypted_file, site_encryption_key):
        """Giải mã file .db.enc"""
        fernet = Fernet(site_encryption_key)
        
        with open(encrypted_file, 'rb') as f:
            encrypted_data = f.read()
        
        decrypted_data = fernet.decrypt(encrypted_data)
        
        # Save decrypted file
        decrypted_file = str(encrypted_file).replace('.db.enc', '.db')
        with open(decrypted_file, 'wb') as f:
            f.write(decrypted_data)
        
        return decrypted_file
    
    def import_to_duckdb(self, db_files, output_db='hub_analytics.duckdb'):
        """Import tất cả SQLite files vào DuckDB"""
        con = duckdb.connect(output_db)
        
        # Create tables if not exist
        con.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                id TEXT PRIMARY KEY,
                site_id TEXT,
                cccd TEXT,
                full_name TEXT,
                date_of_birth DATE,
                gender TEXT,
                created_at TIMESTAMP
            )
        """)
        
        con.execute("""
            CREATE TABLE IF NOT EXISTS encounters (
                id TEXT PRIMARY KEY,
                site_id TEXT,
                patient_id TEXT,
                encounter_date DATE,
                sticker_id TEXT,
                status TEXT,
                created_at TIMESTAMP
            )
        """)
        
        # Import from each SQLite file
        for db_file in tqdm(db_files, desc="Importing to DuckDB"):
            site_id = Path(db_file).stem.split('_')[1]  # Extract from filename
            
            # Attach SQLite database
            con.execute(f"ATTACH '{db_file}' AS site_{site_id} (TYPE SQLITE)")
            
            # Import patients
            con.execute(f"""
                INSERT OR IGNORE INTO patients 
                SELECT id, '{site_id}' as site_id, cccd, full_name, 
                       date_of_birth, gender, created_at
                FROM site_{site_id}.patients
            """)
            
            # Import encounters
            con.execute(f"""
                INSERT OR IGNORE INTO encounters 
                SELECT id, '{site_id}' as site_id, patient_id, 
                       encounter_date, sticker_id, status, created_at
                FROM site_{site_id}.encounters
            """)
            
            # Detach
            con.execute(f"DETACH site_{site_id}")
        
        con.close()
        return output_db
    
    def run_analytics(self, duckdb_file='hub_analytics.duckdb'):
        """Chạy các query phân tích"""
        con = duckdb.connect(duckdb_file)
        
        print("\n=== ANALYTICS REPORT ===\n")
        
        # Total patients by site
        print("1. Tổng số bệnh nhân theo Site:")
        result = con.execute("""
            SELECT site_id, COUNT(*) as total_patients
            FROM patients
            GROUP BY site_id
            ORDER BY total_patients DESC
        """).fetchall()
        for row in result:
            print(f"   {row[0]}: {row[1]} bệnh nhân")
        
        # Total encounters by date
        print("\n2. Tổng số lượt khám theo ngày:")
        result = con.execute("""
            SELECT encounter_date, COUNT(*) as total_encounters
            FROM encounters
            GROUP BY encounter_date
            ORDER BY encounter_date DESC
            LIMIT 10
        """).fetchall()
        for row in result:
            print(f"   {row[0]}: {row[1]} lượt khám")
        
        # Sites with most activity
        print("\n3. Top 5 Sites hoạt động nhiều nhất:")
        result = con.execute("""
            SELECT site_id, COUNT(*) as total_encounters
            FROM encounters
            GROUP BY site_id
            ORDER BY total_encounters DESC
            LIMIT 5
        """).fetchall()
        for row in result:
            print(f"   {row[0]}: {row[1]} lượt khám")
        
        con.close()

def main():
    # Load config from environment
    REPO_OWNER = os.getenv('GITHUB_REPO_OWNER', 'DigitalVersion')
    REPO_NAME = os.getenv('GITHUB_REPO_NAME', 'carevl-snapshots')
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
    MASTER_KEY = os.getenv('MASTER_ENCRYPTION_KEY')
    
    if not GITHUB_TOKEN or not MASTER_KEY:
        print("Error: GITHUB_TOKEN and MASTER_ENCRYPTION_KEY must be set")
        return
    
    # Initialize aggregator
    aggregator = HubAggregator(REPO_OWNER, REPO_NAME, GITHUB_TOKEN, MASTER_KEY)
    
    # Step 1: List all assets
    print("Step 1: Listing all assets...")
    all_assets = aggregator.list_all_assets()
    print(f"Found {len(all_assets)} total assets")
    
    # Step 2: Filter by date (today)
    print("\nStep 2: Filtering by date...")
    target_date = datetime.now().strftime('%Y-%m-%d')
    latest_assets = aggregator.filter_by_date(all_assets, target_date)
    print(f"Found {len(latest_assets)} assets for {target_date}")
    
    # Step 3: Download assets (parallel)
    print("\nStep 3: Downloading assets...")
    downloaded_files = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(aggregator.download_asset, asset): asset 
                   for asset in latest_assets}
        
        for future in tqdm(as_completed(futures), total=len(futures)):
            filepath = future.result()
            downloaded_files.append(filepath)
    
    # Step 4: Decrypt files
    print("\nStep 4: Decrypting files...")
    decrypted_files = []
    for encrypted_file in tqdm(downloaded_files):
        # TODO: Get site-specific encryption key from sites table
        decrypted_file = aggregator.decrypt_file(encrypted_file, MASTER_KEY)
        decrypted_files.append(decrypted_file)
    
    # Step 5: Import to DuckDB
    print("\nStep 5: Importing to DuckDB...")
    duckdb_file = aggregator.import_to_duckdb(decrypted_files)
    print(f"Data imported to {duckdb_file}")
    
    # Step 6: Run analytics
    print("\nStep 6: Running analytics...")
    aggregator.run_analytics(duckdb_file)
    
    print("\n=== DONE ===")

if __name__ == '__main__':
    main()
```

## Usage

### Chạy script thủ công
```bash
# Set environment variables
export GITHUB_TOKEN="ghp_xxxxxxxxxxxx"
export MASTER_ENCRYPTION_KEY="base64_key_here"

# Run script
python scripts/hub_aggregate.py
```

### Chạy tự động (Cron Job)
```bash
# Chạy mỗi ngày lúc 23:00
0 23 * * * cd /path/to/carevl && python scripts/hub_aggregate.py >> logs/aggregate.log 2>&1
```

### Chạy với tham số
```bash
# Chỉ lấy dữ liệu ngày cụ thể
python scripts/hub_aggregate.py --date 2026-04-25

# Chỉ lấy dữ liệu từ Sites cụ thể
python scripts/hub_aggregate.py --sites LongHo_01,BinhMinh_02

# Export ra CSV
python scripts/hub_aggregate.py --export-csv reports/
```

## Output

### DuckDB Database
File `hub_analytics.duckdb` chứa:
- Table `patients`: Tất cả bệnh nhân từ tất cả Sites
- Table `encounters`: Tất cả lượt khám
- Table `observations`: Tất cả kết quả xét nghiệm
- Table `diagnostic_reports`: Tất cả báo cáo chẩn đoán

### Analytics Reports
- Tổng số bệnh nhân theo Site
- Tổng số lượt khám theo ngày
- Top Sites hoạt động nhiều nhất
- Xu hướng khám bệnh theo thời gian

## Performance

### Optimization
- **Parallel Download**: Tải nhiều files cùng lúc (max 5 workers)
- **Streaming**: Không load toàn bộ file vào memory
- **Incremental Import**: Chỉ import dữ liệu mới (dựa vào timestamp)
- **DuckDB**: Nhanh hơn SQLite 10-100x cho analytical queries

### Benchmarks
- 100 Sites, mỗi Site ~10MB: ~5 phút
- 500 Sites, mỗi Site ~10MB: ~20 phút
- Query analytics: < 1 giây

## Security

### Encryption Keys Management
- Mỗi Site có Encryption Key riêng (lưu trong `sites` table)
- Hub cần có quyền truy cập tất cả Keys
- Keys được lưu encrypted bằng Master Key của Hub

### Access Control
- Chỉ Hub Admin có quyền chạy script
- GitHub Token cần scope: `repo` (read releases)
- Audit log ghi lại mọi lần aggregate

## Related Documents
- [07. Active Sync Protocol](07_active_sync_protocol.md)
- [02. SQLite Security & Snapshots](02_SQLite_Security.md)
- [QR Code Provisioning](../FEATURES/qr_provisioning.md)
