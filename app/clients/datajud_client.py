from __future__ import annotations

from typing import Any

import requests

from app.core.config import DATAJUD_API_KEY


class DatajudClient:
    BASE_URL = "https://api-publica.datajud.cnj.jus.br"

    def __init__(self, api_key: str | None = None, timeout: int = 30) -> None:
        self.api_key = api_key or DATAJUD_API_KEY
        self.timeout = timeout

        if not self.api_key:
            raise ValueError("API key do Datajud não informada.")

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"ApiKey {self.api_key}",
            "Content-Type": "application/json",
    }
    def search_all(self,tribunal_alias: str,size: int = 5,) -> dict[str, Any]:
        payload = {
            "size": size,
            "query": {
                "match_all": {}
            }
    }
        return self.search(tribunal_alias, payload)
    

    def search(self, tribunal_alias: str, payload: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.BASE_URL}/{tribunal_alias}/_search"

        response = requests.post(
            url,
            headers=self._headers(),
            json=payload,
            timeout=self.timeout,
        )

        response.raise_for_status()
        return response.json()

    def search_by_process_number(
        self,
        tribunal_alias: str,
        process_number: str,
    ) -> dict[str, Any]:
        payload = {
            "query": {
                "match": {
                    "numeroProcesso": process_number
                }
            }
        }
        return self.search(tribunal_alias, payload)

    def search_by_filters(
        self,
        tribunal_alias: str,
        classe_codigo: int | None = None,
        orgao_julgador_codigo: int | None = None,
    ) -> dict[str, Any]:
        must_conditions: list[dict[str, Any]] = []

        if classe_codigo is not None:
            must_conditions.append({"match": {"classe.codigo": classe_codigo}})

        if orgao_julgador_codigo is not None:
            must_conditions.append(
                {"match": {"orgaoJulgador.codigo": orgao_julgador_codigo}}
            )

        if not must_conditions:
            raise ValueError("Informe ao menos um filtro para a busca.")

        payload = {
            "query": {
                "bool": {
                    "must": must_conditions
                }
            }
        }

        return self.search(tribunal_alias, payload)
    
    