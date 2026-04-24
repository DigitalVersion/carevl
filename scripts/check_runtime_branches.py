from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List


ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "config" / "stations.csv"
REPORT_PATH = ROOT / "reports" / "hub" / "runtime_branch_status.json"
GIT_TIMEOUT_SECONDS = 30
PHASE2_DB_PATHS = [
    "data/carevl.db",
    "carevl.db",
]


def run_git(args: List[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
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


def normalize_bool(value: str) -> bool:
    return (value or "").strip().lower() not in {"0", "false", "no", "n", "off"}


def load_rows() -> List[Dict[str, str]]:
    with open(CSV_PATH, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
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


def fetch_branch(branch_name: str) -> str:
    remote_ref = f"origin/{branch_name}"
    fetch = run_git(["fetch", "origin", branch_name], check=False)
    if fetch.returncode == 0:
        verify = run_git(["rev-parse", "--verify", remote_ref], check=False)
        if verify.returncode == 0:
            return remote_ref

    verify_local = run_git(["rev-parse", "--verify", branch_name], check=False)
    if verify_local.returncode == 0:
        return branch_name

    verify_remote = run_git(["rev-parse", "--verify", remote_ref], check=False)
    if verify_remote.returncode == 0:
        return remote_ref

    stderr = fetch.stderr.strip() or fetch.stdout.strip()
    raise RuntimeError(stderr or f"Khong tim thay branch {branch_name}")


def has_phase2_db(ref_name: str) -> str:
    for path in PHASE2_DB_PATHS:
        result = run_git(["cat-file", "-e", f"{ref_name}:{path}"], check=False)
        if result.returncode == 0:
            return path
    return ""


def build_report() -> Dict[str, object]:
    rows = load_rows()
    results: List[Dict[str, str]] = []
    ok_count = 0

    for row in rows:
        branch_name = branch_for(row)
        if not branch_name:
            continue

        item = {
            "title": row.get("title", ""),
            "station_id": row.get("station_id", ""),
            "branch_name": branch_name,
            "status": "missing_branch",
            "db_path": "",
            "message": "",
        }
        try:
            ref_name = fetch_branch(branch_name)
            db_path = has_phase2_db(ref_name)
            if db_path:
                item["status"] = "ok"
                item["db_path"] = db_path
                item["message"] = "Da co SQLite runtime tren branch."
                ok_count += 1
            else:
                item["status"] = "missing_runtime_db"
                item["message"] = "Branch ton tai nhung chua co carevl.db."
        except Exception as exc:
            item["message"] = str(exc)

        results.append(item)

    return {
        "total_branches": len(results),
        "ok_branches": ok_count,
        "missing_branches": sum(1 for item in results if item["status"] == "missing_branch"),
        "missing_runtime_db": sum(1 for item in results if item["status"] == "missing_runtime_db"),
        "branches": results,
    }


def print_json_console(payload: Dict[str, object]) -> None:
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        print(text)
        return
    except Exception:
        pass
    print(text.encode("ascii", errors="replace").decode("ascii"))


def main() -> int:
    try:
        report = build_report()
        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print_json_console(report)
        return 0
    except Exception as exc:
        print(f"Loi: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
