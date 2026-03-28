from __future__ import annotations

from typing import Any

from app.core.database import get_connection


def add_monitored_process(
    numero_processo: str,
    tribunal_alias: str,
    tribunal_nome: str | None,
    ultima_atualizacao: str | None,
    ultimo_movimento: str | None,
) -> None:
    conn = get_connection()
    cursor = conn.cursor()

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


def get_monitored_process_by_number(
    numero_processo: str,
) -> dict[str, Any] | None:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM monitored_processes
        WHERE numero_processo = ?
        LIMIT 1
    """, (numero_processo,))

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