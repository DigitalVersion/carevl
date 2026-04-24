import json
import sqlite3
import sys
import uuid
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from modules import config_loader
from modules import paths


QUESTIONNAIRE_NAMESPACE = uuid.UUID("7a85873b-d2e5-4740-bc77-a66ecfd89b91")
SCHEMA_SQL_PATH = Path(paths.get_writable_path("sql/phase2_schema.sql"))
DEFAULT_DB_PATH = Path(paths.get_writable_path("data/carevl.db"))


def questionnaire_uuid(package_id: str, version: str) -> str:
    return str(uuid.uuid5(QUESTIONNAIRE_NAMESPACE, f"{package_id}:{version}"))


def ensure_schema(conn: sqlite3.Connection) -> None:
    sql = SCHEMA_SQL_PATH.read_text(encoding="utf-8")
    conn.executescript(sql)


def seed_questionnaires(db_path: Path = DEFAULT_DB_PATH) -> int:
    template = config_loader.load_template_form()
    version = str(template.get("version", "1.0.0") or "1.0.0")
    packages = template.get("packages", [])

    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        ensure_schema(conn)
        seeded = 0
        for package in packages:
            package_id = str(package.get("id", "") or "").strip()
            if not package_id:
                continue

            questionnaire_id = questionnaire_uuid(package_id, version)
            title = str(package.get("label", package_id) or package_id)
            definition_json = json.dumps(package, ensure_ascii=False)
            conn.execute(
                """
                INSERT INTO questionnaires (
                    id,
                    package_id,
                    version,
                    title,
                    status,
                    source_uri,
                    definition_json,
                    created_at,
                    updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
                ON CONFLICT(package_id, version) DO UPDATE SET
                    title = excluded.title,
                    status = excluded.status,
                    source_uri = excluded.source_uri,
                    definition_json = excluded.definition_json,
                    updated_at = datetime('now')
                """,
                (
                    questionnaire_id,
                    package_id,
                    version,
                    title,
                    "active",
                    f"carevl:questionnaire:{package_id}:{version}",
                    definition_json,
                ),
            )
            seeded += 1

        conn.commit()
        return seeded
    finally:
        conn.close()


if __name__ == "__main__":
    total = seed_questionnaires()
    print(f"Seeded questionnaires: {total}")
