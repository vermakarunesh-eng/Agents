import sqlite3
from pathlib import Path

from app.config import get_settings


def db_path() -> Path:
    url = get_settings().database_url
    if url.startswith("sqlite:///"):
        return Path(url.replace("sqlite:///", "", 1))
    return Path("policy_agent.db")


def init_db() -> None:
    path = db_path()
    with sqlite3.connect(path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS reports (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                jurisdiction TEXT NOT NULL,
                created_at TEXT NOT NULL,
                markdown_path TEXT NOT NULL,
                json_path TEXT NOT NULL
            )
            """
        )
        conn.commit()


def save_report_record(report_id: str, title: str, jurisdiction: str, created_at: str, markdown_path: str, json_path: str) -> None:
    init_db()
    with sqlite3.connect(db_path()) as conn:
        conn.execute(
            "INSERT OR REPLACE INTO reports VALUES (?, ?, ?, ?, ?, ?)",
            (report_id, title, jurisdiction, created_at, markdown_path, json_path),
        )
        conn.commit()


def list_report_records() -> list[dict]:
    init_db()
    with sqlite3.connect(db_path()) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM reports ORDER BY created_at DESC").fetchall()
        return [dict(row) for row in rows]

