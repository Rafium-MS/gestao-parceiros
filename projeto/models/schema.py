"""Database schema definition for the delivery management system."""

from __future__ import annotations

from textwrap import dedent

from .database_manager import DatabaseManager

CREATE_TABLE_STATEMENTS = (
    dedent(
        """
        CREATE TABLE IF NOT EXISTS marcas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            codigo_disagua TEXT UNIQUE NOT NULL
        );
        """
    ),
    dedent(
        """
        CREATE TABLE IF NOT EXISTS lojas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            marca_id INTEGER,
            nome TEXT NOT NULL,
            codigo_disagua TEXT UNIQUE NOT NULL,
            local_entrega TEXT,
            municipio TEXT,
            estado TEXT,
            valor_20l REAL,
            valor_10l REAL,
            valor_cx_copo REAL,
            valor_1500ml REAL,
            FOREIGN KEY (marca_id) REFERENCES marcas(id)
        );
        """
    ),
    dedent(
        """
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
        """
    ),
    dedent(
        """
        CREATE TABLE IF NOT EXISTS parceiro_loja (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            parceiro_id INTEGER,
            loja_id INTEGER,
            FOREIGN KEY (parceiro_id) REFERENCES parceiros(id),
            FOREIGN KEY (loja_id) REFERENCES lojas(id),
            UNIQUE(parceiro_id, loja_id)
        );
        """
    ),
    dedent(
        """
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
    ),
)

SCHEMA_SCRIPT = "\n".join(CREATE_TABLE_STATEMENTS)


def initialize_schema(manager: DatabaseManager) -> None:
    """Ensure all tables required by the application exist."""
    manager.execute_script(SCHEMA_SCRIPT)
