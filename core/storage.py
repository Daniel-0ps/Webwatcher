# -*- coding: utf-8 -*-
from __future__ import annotations
import json
import logging
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S%z")

def configure_logging(level: str = "INFO", log_file: Optional[str] = None) -> None:
    lvl = getattr(logging, level.upper(), logging.INFO)
    handlers = [logging.StreamHandler()]
    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file, encoding="utf-8"))
    logging.basicConfig(
        level=lvl,
        format="%(asctime)s %(levelname)-7s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=handlers,
        force=True,
    )

def load_state(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        logging.error("Fichier d’état corrompu (%s) ; ignoré.", path)
        return {}
    except OSError as e:
        logging.error("Impossible de lire l’état (%s) : %s", path, e)
        return {}

def _atomic_write_text(path: Path, data: str) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        f.write(data)
    os.replace(tmp, path)  # atomique sur POSIX & Windows

def save_state(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    _atomic_write_text(path, json.dumps(state, ensure_ascii=False, indent=2))

# --- Historique SQLite (optionnel) ---

def init_history(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS checks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                url TEXT NOT NULL,
                status TEXT NOT NULL,     -- 'initial' | 'no_change' | 'changed' | 'error'
                hash TEXT,
                http_status INTEGER,
                content_length INTEGER,
                note TEXT
            );
            """
        )
        conn.commit()

def write_history(
    db_path: Path, *, url: str, status: str, hash_value: Optional[str],
    http_status: Optional[int], content_length: Optional[int], note: Optional[str]
) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO checks (ts, url, status, hash, http_status, content_length, note)
            VALUES (?, ?, ?, ?, ?, ?, ?);
            """,
            (utc_now_iso(), url, status, hash_value, http_status, content_length, note),
        )
        conn.commit()
