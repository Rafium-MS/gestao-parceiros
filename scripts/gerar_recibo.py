#!/usr/bin/env python3
"""Gera recibo financeiro para um parceiro."""

import argparse
import configparser
from database.db_manager import DatabaseManager
from controllers.financeiro_controller import FinanceiroController


def main() -> None:
    parser = argparse.ArgumentParser(description="Gerar recibo de pagamento")
    parser.add_argument("parceiro_id", type=int, help="ID do parceiro")
    parser.add_argument("data_inicial", help="Data inicial AAAA-MM-DD")
    parser.add_argument("data_final", help="Data final AAAA-MM-DD")
    parser.add_argument("--saida", default="recibo.pdf", help="Arquivo de saída")
    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read("config.ini")
    db_path = config.get("DATABASE", "path")
    db = DatabaseManager(db_path)

    controller = FinanceiroController(db, config)
    sucesso = controller.gerar_recibo_pdf(
        args.parceiro_id, args.data_inicial, args.data_final, args.saida
    )
    db.close_connection()

    if sucesso:
        print(f"Recibo gerado em {args.saida}")
    else:
        print("Falha ao gerar recibo")


if __name__ == "__main__":
    main()