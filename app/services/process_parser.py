from __future__ import annotations

from typing import Any


def _safe_get(data: dict[str, Any], *keys: str, default: Any = None) -> Any:
    current: Any = data

    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key, default)

    return current


def parse_hit(hit: dict[str, Any]) -> dict[str, Any]:
    source = hit.get("_source", {})

    numero_processo = source.get("numeroProcesso", "N/A")

    tribunal = (
        _safe_get(source, "tribunal", "nome")
        or source.get("tribunal", "N/A")
    )

    classe = _safe_get(source, "classe", "nome", default="N/A")
    classe_codigo = _safe_get(source, "classe", "codigo", default="N/A")

    orgao_julgador = _safe_get(source, "orgaoJulgador", "nome", default="N/A")
    orgao_julgador_codigo = _safe_get(source, "orgaoJulgador", "codigo", default="N/A")

    assuntos = source.get("assuntos", [])
    nomes_assuntos = []

    if isinstance(assuntos, list):
        for assunto in assuntos:
            if isinstance(assunto, dict):
                nome = assunto.get("nome")
                if nome:
                    nomes_assuntos.append(nome)

    data_ajuizamento = source.get("dataAjuizamento", "N/A")
    data_ultima_atualizacao = source.get("dataHoraUltimaAtualizacao", "N/A")

    movimentos = source.get("movimentos", [])
    ultimo_movimento = "N/A"

    if isinstance(movimentos, list) and movimentos:
        ultimo = movimentos[-1]
        if isinstance(ultimo, dict):
            ultimo_movimento = ultimo.get("nome", "N/A")

    return {
        "numero_processo": numero_processo,
        "tribunal": tribunal,
        "classe": classe,
        "classe_codigo": classe_codigo,
        "orgao_julgador": orgao_julgador,
        "orgao_julgador_codigo": orgao_julgador_codigo,
        "assuntos": nomes_assuntos,
        "data_ajuizamento": data_ajuizamento,
        "data_ultima_atualizacao": data_ultima_atualizacao,
        "ultimo_movimento": ultimo_movimento,
    }


def parse_search_result(result: dict[str, Any]) -> dict[str, Any]:
    hits_data = result.get("hits", {})
    total = hits_data.get("total", {}).get("value", 0)
    hits = hits_data.get("hits", [])

    parsed_hits = [parse_hit(hit) for hit in hits if isinstance(hit, dict)]

    return {
        "total": total,
        "resultados": parsed_hits,
    }