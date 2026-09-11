"""
SQLite models/connection for storing scan results.
Kept minimal for the hackathon MVP — swap for SQLAlchemy if the schema grows.
"""
import json
import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "ecdat.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS scans (
            scan_id TEXT PRIMARY KEY,
            target_path TEXT,
            started_at TEXT,
            completed_at TEXT,
            status TEXT,
            total_files_scanned INTEGER,
            files_with_findings INTEGER,
            migration_readiness_score REAL,
            findings TEXT,
            summary TEXT
        )
        """
    )
    # Existing local databases predate the coverage split.
    try:
        conn.execute("ALTER TABLE scans ADD COLUMN files_with_findings INTEGER")
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()


def save_scan(scan: dict):
    conn = get_connection()
    conn.execute(
        """
        INSERT OR REPLACE INTO scans
        (scan_id, target_path, started_at, completed_at, status,
         total_files_scanned, files_with_findings, migration_readiness_score, findings, summary)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            scan["scan_id"],
            scan["target_path"],
            scan.get("started_at"),
            scan.get("completed_at"),
            scan.get("status"),
            scan.get("total_files_scanned", 0),
            scan.get("files_with_findings", 0),
            scan.get("migration_readiness_score", 0.0),
            json.dumps(scan.get("findings", [])),
            json.dumps(scan.get("summary", {})),
        ),
    )
    conn.commit()
    conn.close()


def get_scan(scan_id: str) -> dict | None:
    conn = get_connection()
    row = conn.execute("SELECT * FROM scans WHERE scan_id = ?", (scan_id,)).fetchone()
    conn.close()
    if not row:
        return None
    result = dict(row)
    result["findings"] = json.loads(result["findings"])
    result["summary"] = json.loads(result["summary"])
    return result
