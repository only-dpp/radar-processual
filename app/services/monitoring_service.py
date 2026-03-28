from __future__ import annotations

from datetime import datetime, timezone

from app.clients.datajud_client import DatajudClient
from app.core.logger import logger
from app.repositories.monitored_process_repository import (
    add_monitored_process,
    delete_monitored_process,
    list_monitored_processes,
    update_monitored_process,
)
from app.services.process_parser import extract_monitoring_snapshot


def monitor_process(
    tribunal_alias: str,
    numero_processo: str,
) -> bool:
    client = DatajudClient()
    result = client.search_by_process_number(tribunal_alias, numero_processo)

    snapshot = extract_monitoring_snapshot(result)

    if not snapshot:
        raise ValueError("Nenhum processo encontrado para monitoramento.")

    created = add_monitored_process(
        numero_processo=snapshot["numero_processo"],
        tribunal_alias=tribunal_alias,
        tribunal_nome=snapshot["tribunal"],
        ultima_atualizacao=snapshot["ultima_atualizacao"],
        ultimo_movimento=snapshot["ultimo_movimento"],
    )

    if created:
        logger.info(
            "Processo adicionado ao monitoramento | numero=%s tribunal=%s",
            numero_processo,
            tribunal_alias,
        )
    else:
        logger.info(
            "Tentativa de duplicidade no monitoramento | numero=%s tribunal=%s",
            numero_processo,
            tribunal_alias,
        )

    return created


def remove_monitored_process(process_id: int) -> bool:
    removed = delete_monitored_process(process_id)

    if removed:
        logger.info("Processo removido do monitoramento | id=%s", process_id)
    else:
        logger.warning("Tentativa de remoção inválida | id=%s", process_id)

    return removed


def check_monitored_processes() -> list[dict]:
    client = DatajudClient()
    monitored = list_monitored_processes()

    logger.info("Iniciando checagem de processos monitorados | total=%s", len(monitored))

    updates = []
    checked_at = datetime.now(timezone.utc).isoformat()

    for item in monitored:
        process_id = item["id"]
        numero_processo = item["numero_processo"]
        tribunal_alias = item["tribunal_alias"]

        result = client.search_by_process_number(tribunal_alias, numero_processo)
        snapshot = extract_monitoring_snapshot(result)

        if not snapshot:
            continue

        changed = (
            snapshot["ultima_atualizacao"] != item["ultima_atualizacao"]
            or snapshot["ultimo_movimento"] != item["ultimo_movimento"]
        )

        if changed:
            update_data = {
                "id": process_id,
                "numero_processo": numero_processo,
                "tribunal_alias": tribunal_alias,
                "tribunal": snapshot["tribunal"],
                "ultima_atualizacao_antiga": item["ultima_atualizacao"],
                "ultima_atualizacao_nova": snapshot["ultima_atualizacao"],
                "ultimo_movimento_antigo": item["ultimo_movimento"],
                "ultimo_movimento_novo": snapshot["ultimo_movimento"],
                "checked_at": checked_at,
            }

            updates.append(update_data)

            update_monitored_process(
                process_id=process_id,
                ultima_atualizacao=snapshot["ultima_atualizacao"],
                ultimo_movimento=snapshot["ultimo_movimento"],
            )

            logger.info(
                "Atualização detectada | id=%s numero=%s tribunal=%s",
                process_id,
                numero_processo,
                tribunal_alias,
            )

    logger.info("Checagem finalizada | atualizacoes=%s", len(updates))
    return updates