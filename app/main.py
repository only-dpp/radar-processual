from __future__ import annotations

import argparse
import sys

from requests import HTTPError

from app.clients.datajud_client import DatajudClient
from app.core.database import init_db
from app.repositories.monitored_process_repository import list_monitored_processes
from app.services.monitoring_service import (
    check_monitored_processes,
    monitor_process,
    remove_monitored_process,
)
from app.services.process_parser import parse_search_result
from app.services.tribunal_discovery import discover_process_tribunal


def print_processes(result: dict) -> None:
    total = result.get("total", 0)
    resultados = result.get("resultados", [])

    print(f"\nTotal encontrado: {total}\n")

    if not resultados:
        print("Nenhum resultado encontrado.")
        return

    for i, item in enumerate(resultados, start=1):
        assuntos = ", ".join(item["assuntos"]) if item["assuntos"] else "N/A"

        print(f"[{i}] Processo: {item['numero_processo']}")
        print(f"    Tribunal: {item['tribunal']}")
        print(f"    Classe: {item['classe']} (código: {item['classe_codigo']})")
        print(
            f"    Órgão julgador: {item['orgao_julgador']} "
            f"(código: {item['orgao_julgador_codigo']})"
        )
        print(f"    Assuntos: {assuntos}")
        print(f"    Data de ajuizamento: {item['data_ajuizamento']}")
        print(f"    Última atualização: {item['data_ultima_atualizacao']}")
        print(f"    Último movimento: {item['ultimo_movimento']}")
        print("-" * 80)


def print_monitored_processes(items: list[dict]) -> None:
    if not items:
        print("Nenhum processo monitorado.")
        return

    print("\nProcessos monitorados:\n")

    for item in items:
        print(f"[{item['id']}] Processo: {item['numero_processo']}")
        print(f"    Tribunal alias: {item['tribunal_alias']}")
        print(f"    Tribunal nome: {item['tribunal_nome']}")
        print(f"    Última atualização: {item['ultima_atualizacao']}")
        print(f"    Último movimento: {item['ultimo_movimento']}")
        print(f"    Criado em: {item['criado_em']}")
        print("-" * 80)


def print_updates(updates: list[dict]) -> None:
    if not updates:
        print("Nenhuma atualização encontrada.")
        return

    print("\nAtualizações detectadas:\n")

    for item in updates:
        print(f"[{item['id']}] Processo: {item['numero_processo']}")
        print(f"    Tribunal: {item['tribunal']}")
        print(f"    Última atualização antiga: {item['ultima_atualizacao_antiga']}")
        print(f"    Última atualização nova:   {item['ultima_atualizacao_nova']}")
        print(f"    Último movimento antigo:  {item['ultimo_movimento_antigo']}")
        print(f"    Último movimento novo:    {item['ultimo_movimento_novo']}")
        print("-" * 80)


def handle_process_search(args: argparse.Namespace) -> None:
    client = DatajudClient()

    if args.tribunal:
        raw_result = client.search_by_process_number(args.tribunal, args.numero)
        parsed = parse_search_result(raw_result)
        print_processes(parsed)
        return

    alias, raw_result = discover_process_tribunal(client, args.numero)

    if not alias or not raw_result:
        print("Nenhum processo encontrado nos tribunais testados.")
        sys.exit(1)

    print(f"Processo encontrado em: {alias}")
    parsed = parse_search_result(raw_result)
    print_processes(parsed)


def handle_filtered_search(args: argparse.Namespace) -> None:
    client = DatajudClient()

    raw_result = client.search_by_filters(
        tribunal_alias=args.tribunal,
        classe_codigo=args.classe,
        orgao_julgador_codigo=args.orgao,
    )
    parsed = parse_search_result(raw_result)
    print_processes(parsed)


def handle_list_all(args: argparse.Namespace) -> None:
    client = DatajudClient()
    raw_result = client.search_all(args.tribunal, size=args.limite)
    parsed = parse_search_result(raw_result)
    print_processes(parsed)


def handle_monitor_process(args: argparse.Namespace) -> None:
    created = monitor_process(
        tribunal_alias=args.tribunal,
        numero_processo=args.numero,
    )

    if created:
        print("Processo adicionado ao monitoramento com sucesso.")
    else:
        print("Esse processo já está sendo monitorado para esse tribunal.")


def handle_list_monitored(_: argparse.Namespace) -> None:
    items = list_monitored_processes()
    print_monitored_processes(items)


def handle_check_monitored(_: argparse.Namespace) -> None:
    updates = check_monitored_processes()
    print_updates(updates)


def handle_remove_monitored(args: argparse.Namespace) -> None:
    removed = remove_monitored_process(args.id)

    if removed:
        print("Processo removido do monitoramento com sucesso.")
    else:
        print("Nenhum processo monitorado encontrado com esse ID.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="radar-processual",
        description="CLI para consulta e monitoramento processual via Datajud.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    processo_parser = subparsers.add_parser(
        "processo",
        help="Busca um processo pelo número.",
    )
    processo_parser.add_argument("numero", help="Número do processo.")
    processo_parser.add_argument(
        "--tribunal",
        help="Alias do tribunal, ex: api_publica_tjdft",
        required=False,
    )
    processo_parser.set_defaults(func=handle_process_search)

    busca_parser = subparsers.add_parser(
        "buscar",
        help="Busca por filtros estruturados.",
    )
    busca_parser.add_argument(
        "--tribunal",
        required=True,
        help="Alias do tribunal, ex: api_publica_tjdft",
    )
    busca_parser.add_argument(
        "--classe",
        type=int,
        required=False,
        help="Código da classe processual.",
    )
    busca_parser.add_argument(
        "--orgao",
        type=int,
        required=False,
        help="Código do órgão julgador.",
    )
    busca_parser.set_defaults(func=handle_filtered_search)

    listar_parser = subparsers.add_parser(
        "listar",
        help="Lista alguns processos de um tribunal para validação.",
    )
    listar_parser.add_argument(
        "--tribunal",
        required=True,
        help="Alias do tribunal, ex: api_publica_tjdft",
    )
    listar_parser.add_argument(
        "--limite",
        type=int,
        default=5,
        help="Quantidade de resultados para listar.",
    )
    listar_parser.set_defaults(func=handle_list_all)

    monitorar_parser = subparsers.add_parser(
        "monitorar",
        help="Adiciona um processo ao monitoramento.",
    )
    monitorar_parser.add_argument("numero", help="Número do processo.")
    monitorar_parser.add_argument(
        "--tribunal",
        required=True,
        help="Alias do tribunal, ex: api_publica_tjdft",
    )
    monitorar_parser.set_defaults(func=handle_monitor_process)

    monitorados_parser = subparsers.add_parser(
        "monitorados",
        help="Lista os processos monitorados.",
    )
    monitorados_parser.set_defaults(func=handle_list_monitored)

    checar_parser = subparsers.add_parser(
        "checar",
        help="Verifica se houve atualização nos processos monitorados.",
    )
    checar_parser.set_defaults(func=handle_check_monitored)

    remover_parser = subparsers.add_parser(
        "remover",
        help="Remove um processo do monitoramento pelo ID.",
    )
    remover_parser.add_argument(
        "id",
        type=int,
        help="ID interno do processo monitorado.",
    )
    remover_parser.set_defaults(func=handle_remove_monitored)

    return parser


def main() -> None:
    init_db()
    parser = build_parser()
    args = parser.parse_args()

    try:
        args.func(args)
    except HTTPError as exc:
        print(f"Erro HTTP ao consultar o Datajud: {exc}")
        sys.exit(1)
    except ValueError as exc:
        print(f"Erro: {exc}")
        sys.exit(1)
    except Exception as exc:
        print(f"Erro inesperado: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()