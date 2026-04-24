from __future__ import annotations

import csv
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List

import duckdb


ROOT = Path(__file__).resolve().parents[1]
AGGREGATE_DIR = ROOT / "reports" / "aggregate"
HUB_DIR = ROOT / "reports" / "hub"
DB_PATH = HUB_DIR / "carevl_hub.duckdb"


def latest_snapshot_dir() -> Path:
    if not AGGREGATE_DIR.exists():
        raise FileNotFoundError("Chua co reports/aggregate.")
    candidates = sorted(path for path in AGGREGATE_DIR.iterdir() if path.is_dir())
    if not candidates:
        raise FileNotFoundError("Chua co snapshot aggregate nao.")
    return candidates[-1]


def write_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames: List[str] = []
    for row in rows:
        for key in row.keys():
            if key not in fieldnames:
                fieldnames.append(key)

    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def query_rows(conn: duckdb.DuckDBPyConnection, sql: str) -> List[Dict[str, Any]]:
    cursor = conn.execute(sql)
    columns = [item[0] for item in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def build_duckdb(snapshot_dir: Path) -> Dict[str, Any]:
    all_records_path = snapshot_dir / "all-records.json"
    manifest_path = snapshot_dir / "manifest.json"
    if not all_records_path.exists():
        raise FileNotFoundError(f"Khong tim thay file: {all_records_path}")
    if not manifest_path.exists():
        raise FileNotFoundError(f"Khong tim thay file: {manifest_path}")

    HUB_DIR.mkdir(parents=True, exist_ok=True)
    records = json.loads(all_records_path.read_text(encoding="utf-8"))
    conn = duckdb.connect(str(DB_PATH))
    try:
        conn.execute(
            """
            CREATE OR REPLACE TABLE snapshot_manifest AS
            SELECT * FROM read_json_auto(?)
            """,
            [str(manifest_path)],
        )
        if records:
            conn.execute(
                """
                CREATE OR REPLACE TABLE encounters_flat AS
                SELECT * FROM read_json_auto(?)
                """,
                [str(all_records_path)],
            )
        else:
            conn.execute(
                """
                CREATE OR REPLACE TABLE encounters_flat AS
                SELECT
                    ''::VARCHAR AS _station_id,
                    ''::VARCHAR AS station_id,
                    ''::VARCHAR AS _station_title,
                    ''::VARCHAR AS _source_branch,
                    ''::VARCHAR AS sync_state,
                    ''::VARCHAR AS package_id,
                    ''::VARCHAR AS encounter_date,
                    ''::VARCHAR AS full_name
                WHERE FALSE
                """
            )
        conn.execute(
            """
            CREATE OR REPLACE TABLE station_summary AS
            SELECT
                coalesce(_station_id, station_id, '') AS station_id,
                coalesce(_station_title, '') AS station_title,
                _source_branch AS branch_name,
                count(*) AS encounter_count,
                count(*) FILTER (WHERE lower(coalesce(sync_state, '')) = 'synced') AS synced_count,
                count(*) FILTER (WHERE lower(coalesce(sync_state, '')) <> 'synced') AS pending_count,
                count(DISTINCT full_name) AS patient_name_count
            FROM encounters_flat
            GROUP BY 1, 2, 3
            ORDER BY encounter_count DESC, branch_name
            """
        )
        conn.execute(
            """
            CREATE OR REPLACE TABLE package_summary AS
            SELECT
                coalesce(package_id, '') AS package_id,
                count(*) AS encounter_count,
                count(DISTINCT coalesce(_station_id, station_id, '')) AS station_count
            FROM encounters_flat
            GROUP BY 1
            ORDER BY encounter_count DESC, package_id
            """
        )
        conn.execute(
            """
            CREATE OR REPLACE TABLE daily_summary AS
            SELECT
                coalesce(encounter_date, '') AS encounter_date,
                count(*) AS encounter_count,
                count(DISTINCT coalesce(_station_id, station_id, '')) AS station_count
            FROM encounters_flat
            GROUP BY 1
            ORDER BY encounter_date DESC
            """
        )

        station_rows = query_rows(conn, "SELECT * FROM station_summary")
        package_rows = query_rows(conn, "SELECT * FROM package_summary")
        daily_rows = query_rows(conn, "SELECT * FROM daily_summary")
        totals_row = conn.execute(
            """
            SELECT
                count(*) AS encounter_count,
                count(DISTINCT coalesce(_source_branch, '')) AS branch_count,
                count(DISTINCT coalesce(_station_id, station_id, '')) AS station_count
            FROM encounters_flat
            """
        ).fetchone()

        write_csv(HUB_DIR / "station_summary.csv", station_rows)
        write_csv(HUB_DIR / "package_summary.csv", package_rows)
        write_csv(HUB_DIR / "daily_summary.csv", daily_rows)

        readme = [
            "# CareVL Hub DuckDB",
            "",
            f"- Snapshot nguon: `{snapshot_dir.name}`",
            f"- File DB: `{DB_PATH.name}`",
            f"- Tong luot kham: `{totals_row[0]}`",
            f"- Tong branch: `{totals_row[1]}`",
            f"- Tong tram: `{totals_row[2]}`",
            "",
            "## Bang chinh",
            "",
            "- `encounters_flat`: luot kham da phang hoa de thong ke",
            "- `snapshot_manifest`: metadata tung branch trong snapshot",
            "- `station_summary`: tong hop theo tram/branch",
            "- `package_summary`: tong hop theo goi kham",
            "- `daily_summary`: tong hop theo ngay",
            "",
        ]
        (HUB_DIR / "README.md").write_text("\n".join(readme), encoding="utf-8")

        return {
            "snapshot": snapshot_dir.name,
            "db_path": str(DB_PATH),
            "encounter_count": totals_row[0],
            "branch_count": totals_row[1],
            "station_count": totals_row[2],
        }
    finally:
        conn.close()


def main() -> int:
    try:
        snapshot_dir = latest_snapshot_dir()
        summary = build_duckdb(snapshot_dir)
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        print(f"Loi: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
