from __future__ import annotations

import csv
import json
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = ROOT / "config"
CSV_PATH = CONFIG_DIR / "stations.csv"
REPORTS_DIR = ROOT / "reports" / "aggregate"
GIT_TIMEOUT_SECONDS = 30
PHASE2_DB_PATHS = [
    "data/carevl.db",
    "carevl.db",
]


def normalize_bool(value: str) -> bool:
    return (value or "").strip().lower() not in {"0", "false", "no", "n", "off"}


def run_git_text(args: List[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=GIT_TIMEOUT_SECONDS,
        check=False,
    )
    if check and completed.returncode != 0:
        stderr = completed.stderr.strip() or completed.stdout.strip()
        raise RuntimeError(f"Git {' '.join(args)} that bai: {stderr}")
    return completed


def run_git_bytes(args: List[str], *, check: bool = True) -> subprocess.CompletedProcess[bytes]:
    completed = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        capture_output=True,
        text=False,
        timeout=GIT_TIMEOUT_SECONDS,
        check=False,
    )
    if check and completed.returncode != 0:
        stderr = completed.stderr.decode("utf-8", errors="replace").strip()
        stdout = completed.stdout.decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"Git {' '.join(args)} that bai: {stderr or stdout}")
    return completed


def load_rows() -> List[Dict[str, str]]:
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"Khong tim thay file: {CSV_PATH}")

    with open(CSV_PATH, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError("File CSV khong co header.")

        rows: List[Dict[str, str]] = []
        for row in reader:
            cleaned = {key.strip(): (value or "").strip() for key, value in row.items() if key}
            if normalize_bool(cleaned.get("active", "true")):
                rows.append(cleaned)
        return rows


def branch_for(row: Dict[str, str]) -> str:
    branch_name = row.get("branch_name", "").strip()
    if branch_name:
        return branch_name
    github_username = row.get("github_username", "").strip()
    if github_username:
        return f"user/{github_username}"
    return ""


def station_key(row: Dict[str, str], branch_name: str) -> str:
    station_id = row.get("station_id", "").strip()
    if station_id:
        return station_id
    if branch_name == "main":
        return "HUB"
    return branch_name.replace("/", "__")


def fetch_branch(branch_name: str) -> Tuple[str, str]:
    remote_ref = f"origin/{branch_name}"
    fetch_ok = False
    fetch_error = ""

    try:
        run_git_text(["fetch", "origin", branch_name], check=True)
        fetch_ok = True
    except Exception as exc:
        fetch_error = str(exc)

    if fetch_ok:
        verify_remote = run_git_text(["rev-parse", "--verify", remote_ref], check=False)
        if verify_remote.returncode == 0:
            return remote_ref, ""

    verify_local = run_git_text(["rev-parse", "--verify", branch_name], check=False)
    if verify_local.returncode == 0:
        return branch_name, fetch_error

    verify_remote = run_git_text(["rev-parse", "--verify", remote_ref], check=False)
    if verify_remote.returncode == 0:
        return remote_ref, fetch_error

    raise RuntimeError(f"Khong tim thay branch/ref cho '{branch_name}'. {fetch_error}".strip())


def git_object_exists(ref_name: str, file_path: str) -> bool:
    completed = run_git_text(["cat-file", "-e", f"{ref_name}:{file_path}"], check=False)
    return completed.returncode == 0


def get_commit_hash(ref_name: str) -> str:
    completed = run_git_text(["rev-parse", ref_name], check=False)
    if completed.returncode != 0:
        return ""
    return completed.stdout.strip()


def detect_db_in_ref(ref_name: str) -> Tuple[str, str]:
    for path in PHASE2_DB_PATHS:
        if git_object_exists(ref_name, path):
            return "phase2", path
    raise RuntimeError(f"Khong tim thay file runtime SQLite (carevl.db) trong ref {ref_name}.")


def extract_db_from_ref(ref_name: str, db_git_path: str, output_path: Path) -> None:
    completed = run_git_bytes(["show", f"{ref_name}:{db_git_path}"], check=True)
    output_path.write_bytes(completed.stdout)


def table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ? LIMIT 1",
        (table_name,),
    ).fetchone()
    return row is not None


def safe_json_load(text: Any) -> Dict[str, Any]:
    if not text:
        return {}
    try:
        value = json.loads(text)
    except (TypeError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def flatten_data(prefix: str, data: Dict[str, Any]) -> Dict[str, str]:
    result: Dict[str, str] = {}
    for key, value in data.items():
        name = f"{prefix}.{key}" if prefix else str(key)
        if isinstance(value, dict):
            result.update(flatten_data(name, value))
        else:
            result[name] = "" if value is None else str(value)
    return result


def read_phase2_records(db_path: Path) -> List[Dict[str, Any]]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            """
            SELECT
                e.id AS encounter_id,
                e.patient_id,
                p.full_name,
                p.birth_date,
                p.gender_text,
                p.address_line,
                e.package_id,
                e.encounter_date,
                e.author,
                e.station_id,
                e.commune_code,
                e.sync_state,
                e.classification_display,
                e.created_at,
                e.updated_at,
                qr.response_json,
                qr.source_record_json
            FROM encounters e
            LEFT JOIN patients p ON p.id = e.patient_id
            LEFT JOIN questionnaire_responses qr ON qr.encounter_id = e.id
            ORDER BY e.encounter_date, e.created_at, e.id
            """
        ).fetchall()

        identifier_map: Dict[str, Dict[str, str]] = {}
        for row in conn.execute(
            """
            SELECT patient_id, identifier_type, value
            FROM patient_identifiers
            ORDER BY is_primary DESC, created_at ASC, id ASC
            """
        ).fetchall():
            patient_id = str(row["patient_id"] or "")
            bucket = identifier_map.setdefault(patient_id, {})
            key = str(row["identifier_type"] or "").strip()
            if key and key not in bucket:
                bucket[key] = str(row["value"] or "").strip()

        records: List[Dict[str, Any]] = []
        for row in rows:
            source_record = safe_json_load(row["source_record_json"])
            source_data = source_record.get("data", {}) if isinstance(source_record.get("data"), dict) else {}
            flat_data = flatten_data("", source_data)
            identifiers = identifier_map.get(str(row["patient_id"] or ""), {})
            record: Dict[str, Any] = {
                "schema_version": "phase2",
                "record_id": str(row["encounter_id"] or ""),
                "encounter_id": str(row["encounter_id"] or ""),
                "patient_id": str(row["patient_id"] or ""),
                "full_name": str(row["full_name"] or ""),
                "birth_date": str(row["birth_date"] or ""),
                "gender_text": str(row["gender_text"] or ""),
                "address_line": str(row["address_line"] or ""),
                "package_id": str(row["package_id"] or ""),
                "encounter_date": str(row["encounter_date"] or ""),
                "author": str(row["author"] or ""),
                "station_id": str(row["station_id"] or ""),
                "commune_code": str(row["commune_code"] or ""),
                "sync_state": str(row["sync_state"] or ""),
                "synced": str(row["sync_state"] or "") == "synced",
                "classification_display": str(row["classification_display"] or ""),
                "created_at": str(row["created_at"] or ""),
                "updated_at": str(row["updated_at"] or ""),
                "identifier_primary": identifiers.get("cccd_or_bhyt", ""),
                "identifier_cccd": identifiers.get("cccd", ""),
                "identifier_vneid": identifiers.get("vneid", ""),
                "identifier_vneid_or_local": identifiers.get("vneid_or_local", ""),
                "source_record_json": row["source_record_json"] or "",
                "response_json": row["response_json"] or "",
            }
            record.update(flat_data)
            records.append(record)
        return records
    finally:
        conn.close()


def inspect_db(db_path: Path, schema_version: str) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    conn = sqlite3.connect(db_path)
    try:
        schema_meta = ""
        if table_exists(conn, "schema_meta"):
            row = conn.execute(
                "SELECT value FROM schema_meta WHERE key = 'phase2_schema_version' LIMIT 1"
            ).fetchone()
            if row:
                schema_meta = str(row[0] or "")

        table_counts: Dict[str, int] = {}
        for table_name in (
            "patients",
            "patient_identifiers",
            "encounters",
            "questionnaire_responses",
            "observations",
            "conditions",
        ):
            if table_exists(conn, table_name):
                count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
                table_counts[table_name] = int(count)
    finally:
        conn.close()

    records = read_phase2_records(db_path)
    metadata = {
        "schema_version": schema_version,
        "phase2_schema_version": schema_meta,
        "table_counts": table_counts,
        "record_count": len(records),
    }
    return records, metadata


def build_branch_snapshot(row: Dict[str, str]) -> Dict[str, Any]:
    branch_name = branch_for(row)
    if not branch_name:
        raise ValueError("Dong tram khong co branch_name/github_username.")

    ref_name = ""
    fetch_error = ""
    missing_branch = False
    records: List[Dict[str, Any]] = []
    db_git_path = ""
    schema_version = ""
    metadata: Dict[str, Any] = {"table_counts": {}, "phase2_schema_version": ""}

    temp_dir = Path(tempfile.mkdtemp(prefix="carevl-aggregate-"))
    try:
        try:
            ref_name, fetch_error = fetch_branch(branch_name)
            schema_version, db_git_path = detect_db_in_ref(ref_name)
            temp_db_path = temp_dir / Path(db_git_path).name
            extract_db_from_ref(ref_name, db_git_path, temp_db_path)
            records, metadata = inspect_db(temp_db_path, schema_version)
        except Exception as exc:
            fetch_error = str(exc)
            missing_branch = True
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    for record in records:
        record["_source_branch"] = branch_name
        record["_source_ref"] = ref_name
        record["_station_title"] = row.get("title", "")
        record["_station_id"] = row.get("station_id", "")
        record["_commune_code"] = row.get("commune_code", "")
        record["_schema_version"] = schema_version
        record["_db_git_path"] = db_git_path

    return {
        "branch_name": branch_name,
        "ref_name": ref_name,
        "commit": get_commit_hash(ref_name) if ref_name else "",
        "title": row.get("title", ""),
        "station_id": row.get("station_id", ""),
        "commune_code": row.get("commune_code", ""),
        "record_count": len(records),
        "records": records,
        "fetch_warning": fetch_error,
        "missing_branch": missing_branch,
        "schema_version": schema_version,
        "db_git_path": db_git_path,
        "table_counts": metadata.get("table_counts", {}),
        "phase2_schema_version": metadata.get("phase2_schema_version", ""),
    }


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


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


def compact_record_for_json(record: Dict[str, Any]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in record.items():
        if key in {"source_record_json", "response_json"} and isinstance(value, str) and len(value) > 5000:
            result[key] = value[:5000]
            continue
        result[key] = value
    return result


def export_snapshot(snapshots: List[Dict[str, Any]]) -> Path:
    stamp = datetime.now().strftime("%Y-%m-%d")
    output_dir = REPORTS_DIR / stamp
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest: List[Dict[str, Any]] = []
    all_records: List[Dict[str, Any]] = []
    by_station_rows: List[Dict[str, Any]] = []

    by_station_dir = output_dir / "by-station"
    by_branch_dir = output_dir / "by-branch"

    for snapshot in snapshots:
        manifest_item = {
            "branch_name": snapshot["branch_name"],
            "ref_name": snapshot["ref_name"],
            "commit": snapshot["commit"],
            "title": snapshot["title"],
            "station_id": snapshot["station_id"],
            "commune_code": snapshot["commune_code"],
            "record_count": snapshot["record_count"],
            "fetch_warning": snapshot["fetch_warning"],
            "missing_branch": snapshot["missing_branch"],
            "schema_version": snapshot["schema_version"],
            "db_git_path": snapshot["db_git_path"],
            "phase2_schema_version": snapshot["phase2_schema_version"],
            "table_counts": snapshot["table_counts"],
        }
        manifest.append(manifest_item)

        station_slug = station_key(snapshot, snapshot["branch_name"])
        branch_records = [compact_record_for_json(record) for record in snapshot["records"]]
        write_json(by_station_dir / f"{station_slug}.json", branch_records)
        write_json(by_branch_dir / f"{snapshot['branch_name'].replace('/', '__')}.json", branch_records)

        by_station_rows.append(
            {
                "station_id": snapshot["station_id"],
                "title": snapshot["title"],
                "branch_name": snapshot["branch_name"],
                "commit": snapshot["commit"],
                "record_count": snapshot["record_count"],
                "schema_version": snapshot["schema_version"],
                "db_git_path": snapshot["db_git_path"],
                "missing_branch": snapshot["missing_branch"],
            }
        )

        all_records.extend(snapshot["records"])

    write_json(output_dir / "manifest.json", manifest)
    write_json(output_dir / "all-records.json", [compact_record_for_json(record) for record in all_records])
    write_csv(output_dir / "all-records.csv", all_records)
    write_csv(output_dir / "stations-summary.csv", by_station_rows)

    summary_md = [
        "# Aggregate Snapshot",
        "",
        f"- Ngay tao: `{stamp}`",
        f"- Tong branch: `{len(snapshots)}`",
        f"- Tong luot kham: `{len(all_records)}`",
        "",
        "## Branch Summary",
        "",
    ]
    for item in manifest:
        summary_md.append(
            f"- `{item['branch_name']}` | `{item['station_id']}` | schema={item['schema_version'] or 'unknown'} | records={item['record_count']}"
        )
    summary_md.append("")
    (output_dir / "README.md").write_text("\n".join(summary_md), encoding="utf-8")

    return output_dir


def main() -> int:
    try:
        rows = load_rows()
        snapshots: List[Dict[str, Any]] = []
        for row in rows:
            branch_name = branch_for(row)
            if not branch_name:
                continue
            snapshots.append(build_branch_snapshot(row))

        output_dir = export_snapshot(snapshots)
        total_records = sum(item["record_count"] for item in snapshots)
        phase2_count = sum(1 for item in snapshots if item.get("schema_version") == "phase2")
        print(f"Da tao aggregate snapshot: {output_dir}")
        print(f"So branch da gom: {len(snapshots)}")
        print(f"So branch phase2: {phase2_count}")
        print(f"Tong so luot kham: {total_records}")
        return 0
    except Exception as exc:
        print(f"Loi: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
