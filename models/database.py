"""Database utilities for the gestão de parceiros application."""

from __future__ import annotations

from pathlib import Path
import sqlite3
from typing import Tuple


DEFAULT_DB_PATH = Path("data") / "entregas.db"


def init_database(db_path: str | Path | None = None) -> Tuple[sqlite3.Connection, sqlite3.Cursor]:
    """Initialise the SQLite database and return the connection and cursor.

    The function ensures the database directory exists, creates the required
    tables when they are missing and returns an open connection alongside a
    cursor that can be reused by repositories.
    """

    path = Path(db_path) if db_path else DEFAULT_DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(path)
    cursor = connection.cursor()

    cursor.executescript(
        """
        CREATE TABLE IF NOT EXISTS marcas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            codigo_disagua TEXT UNIQUE
        );

        CREATE TABLE IF NOT EXISTS lojas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            marca_id INTEGER,
            nome TEXT NOT NULL,
            codigo_disagua TEXT UNIQUE,
            local_entrega TEXT,
            municipio TEXT,
            estado TEXT,
            valor_20l REAL,
            valor_10l REAL,
            valor_cx_copo REAL,
            valor_1500ml REAL,
            FOREIGN KEY (marca_id) REFERENCES marcas(id)
        );

        CREATE TABLE IF NOT EXISTS parceiros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cidade TEXT,
            estado TEXT,
            nome_parceiro TEXT NOT NULL,
            distribuidora TEXT,
            cnpj TEXT,
            telefone TEXT,
            email TEXT,
            dia_pagamento INTEGER,
            banco TEXT,
            agencia TEXT,
            conta TEXT,
            chave_pix TEXT,
            valor_20l REAL,
            valor_10l REAL,
            valor_cx_copo REAL,
            valor_1500ml REAL
        );

        CREATE TABLE IF NOT EXISTS parceiro_loja (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            parceiro_id INTEGER,
            loja_id INTEGER,
            FOREIGN KEY (parceiro_id) REFERENCES parceiros(id),
            FOREIGN KEY (loja_id) REFERENCES lojas(id),
            UNIQUE(parceiro_id, loja_id)
        );

        CREATE TABLE IF NOT EXISTS comprovantes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            parceiro_id INTEGER,
            loja_id INTEGER,
            data_entrega DATE,
            qtd_20l INTEGER DEFAULT 0,
            qtd_10l INTEGER DEFAULT 0,
            qtd_cx_copo INTEGER DEFAULT 0,
            qtd_1500ml INTEGER DEFAULT 0,
            assinatura TEXT,
            arquivo_comprovante TEXT,
            data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (parceiro_id) REFERENCES parceiros(id),
            FOREIGN KEY (loja_id) REFERENCES lojas(id)
        );
        """
    )

    connection.commit()
    return connection, cursor

