from __future__ import annotations

import argparse
import sys

from app.clients.datajud_client import DatajudClient
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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="jurispulse",
        description="CLI para consulta pública de dados processuais via Datajud.",
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

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()