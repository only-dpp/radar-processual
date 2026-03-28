from __future__ import annotations

import sqlite3
from typing import Any

from app.core.database import get_connection


def add_monitored_process(
    numero_processo: str,
    tribunal_alias: str,
    tribunal_nome: str | None,
    ultima_atualizacao: str | None,
    ultimo_movimento: str | None,
) -> bool:
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO monitored_processes (
                numero_processo,
                tribunal_alias,
                tribunal_nome,
                ultima_atualizacao,
                ultimo_movimento
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            numero_processo,
            tribunal_alias,
            tribunal_nome,
            ultima_atualizacao,
            ultimo_movimento,
        ))
        conn.commit()
        return True

    except sqlite3.IntegrityError:
        return False

    finally:
        conn.close()


def list_monitored_processes() -> list[dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM monitored_processes
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_monitored_process_by_number_and_alias(
    numero_processo: str,
    tribunal_alias: str,
) -> dict[str, Any] | None:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM monitored_processes
        WHERE numero_processo = ?
          AND tribunal_alias = ?
        LIMIT 1
    """, (numero_processo, tribunal_alias))

    row = cursor.fetchone()
    conn.close()

    return dict(row) if row else None


def get_monitored_process_by_id(process_id: int) -> dict[str, Any] | None:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM monitored_processes
        WHERE id = ?
        LIMIT 1
    """, (process_id,))

    row = cursor.fetchone()
    conn.close()

    return dict(row) if row else None


def update_monitored_process(
    process_id: int,
    ultima_atualizacao: str | None,
    ultimo_movimento: str | None,
) -> None:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE monitored_processes
        SET ultima_atualizacao = ?, ultimo_movimento = ?
        WHERE id = ?
    """, (
        ultima_atualizacao,
        ultimo_movimento,
        process_id,
    ))

    conn.commit()
    conn.close()


def delete_monitored_process(process_id: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM monitored_processes
        WHERE id = ?
    """, (process_id,))

    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()

    return deleted