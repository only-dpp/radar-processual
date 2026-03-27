from __future__ import annotations

from typing import Any

from app.clients.datajud_client import DatajudClient


TRIBUNAIS_INICIAIS = [
    "api_publica_tjsp",
    "api_publica_tjrj",
    "api_publica_tjmg",
    "api_publica_tjdft",
    "api_publica_trf1",
    "api_publica_trf3",
    "api_publica_trt2",
    "api_publica_stj",
]


def discover_process_tribunal(
    client: DatajudClient,
    process_number: str,
    aliases: list[str] | None = None,
) -> tuple[str | None, dict[str, Any] | None]:
    aliases = aliases or TRIBUNAIS_INICIAIS

    for alias in aliases:
        try:
            result = client.search_by_process_number(alias, process_number)
            total = result.get("hits", {}).get("total", {}).get("value", 0)

            if total > 0:
                return alias, result

        except Exception:
            continue

    return None, None