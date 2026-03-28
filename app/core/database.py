from __future__ import annotations

import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / "radar_processual.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS monitored_processes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_processo TEXT NOT NULL,
            tribunal_alias TEXT NOT NULL,
            tribunal_nome TEXT,
            ultima_atualizacao TEXT,
            ultimo_movimento TEXT,
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()