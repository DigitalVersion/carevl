"""DuckDB aggregator for CareVL Hub"""

import duckdb
from pathlib import Path
from typing import List, Optional


class DuckDBAggregator:
    """Aggregate data from multiple SQLite databases using DuckDB"""
    
    def __init__(self, memory_limit: str = "4GB", threads: int = 4):
        self.memory_limit = memory_limit
        self.threads = threads
        self.conn: Optional[duckdb.DuckDBPyConnection] = None
    
    def connect(self, db_path: Optional[Path] = None):
        """Connect to DuckDB (in-memory or file-based)"""
        if db_path:
            self.conn = duckdb.connect(str(db_path))
        else:
            self.conn = duckdb.connect(":memory:")
        
        # Set configuration
        self.conn.execute(f"PRAGMA memory_limit='{self.memory_limit}'")
        self.conn.execute(f"PRAGMA threads={self.threads}")
    
    def attach_databases(self, db_files: List[Path]):
        """Attach multiple SQLite databases"""
        for i, db_file in enumerate(db_files):
            alias = f"s{i:03d}"
            self.conn.execute(f"ATTACH '{db_file}' AS {alias} (TYPE SQLITE)")
            print(f"Attached: {db_file.name} as {alias}")
    
    def aggregate_patients(self) -> int:
        """Aggregate patients from all databases"""
        # Get list of attached databases
        dbs = self.conn.execute("PRAGMA database_list").fetchall()
        db_aliases = [db[1] for db in dbs if db[1].startswith("s")]
        
        # Build UNION ALL query
        union_queries = [f"SELECT * FROM {alias}.patients" for alias in db_aliases]
        query = " UNION ALL ".join(union_queries)
        
        # Create aggregated table
        self.conn.execute(f"CREATE TABLE hub_patients AS {query}")
        
        count = self.conn.execute("SELECT COUNT(*) FROM hub_patients").fetchone()[0]
        print(f"Aggregated {count} patients")
        return count
    
    def aggregate_encounters(self) -> int:
        """Aggregate encounters from all databases"""
        dbs = self.conn.execute("PRAGMA database_list").fetchall()
        db_aliases = [db[1] for db in dbs if db[1].startswith("s")]
        
        union_queries = [f"SELECT * FROM {alias}.encounters" for alias in db_aliases]
        query = " UNION ALL ".join(union_queries)
        
        self.conn.execute(f"CREATE TABLE hub_encounters AS {query}")
        
        count = self.conn.execute("SELECT COUNT(*) FROM hub_encounters").fetchone()[0]
        print(f"Aggregated {count} encounters")
        return count
    
    def aggregate_observations(self) -> int:
        """Aggregate observations from all databases"""
        dbs = self.conn.execute("PRAGMA database_list").fetchall()
        db_aliases = [db[1] for db in dbs if db[1].startswith("s")]
        
        union_queries = [f"SELECT * FROM {alias}.observations" for alias in db_aliases]
        query = " UNION ALL ".join(union_queries)
        
        self.conn.execute(f"CREATE TABLE hub_observations AS {query}")
        
        count = self.conn.execute("SELECT COUNT(*) FROM hub_observations").fetchone()[0]
        print(f"Aggregated {count} observations")
        return count
    
    def export_to_parquet(self, output_dir: Path):
        """Export aggregated tables to Parquet files"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        tables = ["hub_patients", "hub_encounters", "hub_observations"]
        for table in tables:
            output_file = output_dir / f"{table}.parquet"
            self.conn.execute(f"COPY {table} TO '{output_file}' (FORMAT PARQUET)")
            print(f"Exported: {output_file}")
    
    def run_query(self, sql: str):
        """Run custom SQL query"""
        return self.conn.execute(sql).fetchall()
    
    def close(self):
        """Close DuckDB connection"""
        if self.conn:
            self.conn.close()
