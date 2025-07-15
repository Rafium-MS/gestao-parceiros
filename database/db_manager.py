#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Gerenciador de Banco de Dados
-----------------------------
Responsável por gerenciar a conexão com o banco de dados e executar operações.
"""

import os
import sqlite3
import datetime
import shutil
import logging


class DatabaseManager:
    """Classe para gerenciar operações com o banco de dados SQLite."""

    def __init__(self, db_path):
        """
        Inicializa o gerenciador de banco de dados.

        Args:
            db_path (str): Caminho para o arquivo de banco de dados.
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.logger = logging.getLogger(__name__)

        # Garantir que o diretório do banco de dados existe
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)

        # Conectar ao banco de dados
        self.connect()

    def connect(self):
        """Estabelece a conexão com o banco de dados."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.execute("PRAGMA foreign_keys = ON")  # Habilitar chaves estrangeiras
            self.cursor = self.conn.cursor()
            self.logger.info(f"Conexão estabelecida com o banco de dados: {self.db_path}")
        except sqlite3.Error as e:
            self.logger.error(f"Erro ao conectar ao banco de dados: {str(e)}")
            raise

    def close_connection(self):
        """Fecha a conexão com o banco de dados."""
        if self.conn:
            self.conn.close()
            self.logger.info("Conexão com o banco de dados fechada")

    def commit(self):
        """Salva as mudanças no banco de dados."""
        if self.conn:
            self.conn.commit()

    def execute(self, query, params=()):
        """
        Executa uma consulta SQL.

        Args:
            query (str): Consulta SQL a ser executada.
            params (tuple, optional): Parâmetros para a consulta. Padrão é ().

        Returns:
            cursor: Cursor com o resultado da consulta.
        """
        try:
            return self.cursor.execute(query, params)
        except sqlite3.Error as e:
            self.logger.error(f"Erro ao executar consulta: {str(e)}")
            self.logger.debug(f"Consulta: {query}, Parâmetros: {params}")
            raise

    def executemany(self, query, params_list):
        """
        Executa uma consulta SQL múltiplas vezes com diferentes parâmetros.

        Args:
            query (str): Consulta SQL a ser executada.
            params_list (list): Lista de tuplas de parâmetros.

        Returns:
            cursor: Cursor com o resultado da consulta.
        """
        try:
            return self.cursor.executemany(query, params_list)
        except sqlite3.Error as e:
            self.logger.error(f"Erro ao executar consulta múltipla: {str(e)}")
            raise

    def fetchall(self):
        """
        Obtém todos os resultados da última consulta.

        Returns:
            list: Lista de resultados.
        """
        return self.cursor.fetchall()

    def fetchone(self):
        """
        Obtém um resultado da última consulta.

        Returns:
            tuple: Um resultado.
        """
        return self.cursor.fetchone()

    def last_insert_rowid(self):
        """
        Obtém o ID da última linha inserida.

        Returns:
            int: ID da última inserção.
        """
        return self.cursor.lastrowid

    def backup_database(self, destination=None):
        """
        Cria um backup do banco de dados.

        Args:
            destination (str, optional): Caminho para o arquivo de backup.
                                        Se None, um nome será gerado automaticamente.

        Returns:
            str: Caminho para o arquivo de backup.
        """
        if not destination:
            backup_dir = os.path.join(os.path.dirname(self.db_path), "backups")
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)

            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            destination = os.path.join(backup_dir, f"backup_{timestamp}.db")

        try:
            # Fechar a conexão atual para evitar problemas de acesso ao arquivo
            self.close_connection()

            # Copiar o arquivo do banco de dados
            shutil.copy2(self.db_path, destination)

            # Reconectar
            self.connect()

            self.logger.info(f"Backup criado com sucesso: {destination}")
            return destination
        except Exception as e:
            self.logger.error(f"Erro ao criar backup: {str(e)}")
            # Tentar reconectar em caso de erro
            self.connect()
            raise

    def restore_database(self, backup_path):
        """
        Restaura o banco de dados a partir de um backup.

        Args:
            backup_path (str): Caminho para o arquivo de backup.

        Returns:
            bool: True se a restauração foi bem-sucedida, False caso contrário.
        """
        if not os.path.exists(backup_path):
            self.logger.error(f"Arquivo de backup não encontrado: {backup_path}")
            return False

        try:
            # Fechar a conexão atual
            self.close_connection()

            # Fazer backup do banco atual antes de substituir
            current_backup = self.db_path + ".bak"
            shutil.copy2(self.db_path, current_backup)

            # Substituir o banco de dados pelo backup
            shutil.copy2(backup_path, self.db_path)

            # Reconectar
            self.connect()

            self.logger.info(f"Banco de dados restaurado a partir de: {backup_path}")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao restaurar banco de dados: {str(e)}")

            # Tentar restaurar o backup do banco atual em caso de falha
            try:
                if os.path.exists(current_backup):
                    shutil.copy2(current_backup, self.db_path)
            except:
                pass

            # Tentar reconectar
            self.connect()
            return False

    def setup_database(self):
        """Configura o banco de dados criando as tabelas necessárias se não existirem."""
        try:
            # Tabela de parceiros
            self.execute('''
            CREATE TABLE IF NOT EXISTS parceiros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                cpf TEXT UNIQUE,
                telefone TEXT,
                email TEXT,
                endereco TEXT,
                data_cadastro TEXT
            )
            ''')

            # Tabela de lojas
            self.execute('''
            CREATE TABLE IF NOT EXISTS lojas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                cnpj TEXT UNIQUE,
                telefone TEXT,
                email TEXT,
                endereco TEXT,
                contato TEXT,
                data_cadastro TEXT
            )
            ''')

            # Tabela de comprovantes
            self.execute('''
            CREATE TABLE IF NOT EXISTS comprovantes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                parceiro_id INTEGER,
                loja_id INTEGER,
                data_entrega TEXT,
                caminho_arquivo TEXT,
                observacoes TEXT,
                data_cadastro TEXT,
                FOREIGN KEY (parceiro_id) REFERENCES parceiros (id),
                FOREIGN KEY (loja_id) REFERENCES lojas (id)
            )
            ''')

            # Tabela de associações
            self.execute('''
            CREATE TABLE IF NOT EXISTS associacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                parceiro_id INTEGER,
                loja_id INTEGER,
                data_associacao TEXT,
                status TEXT,
                FOREIGN KEY (parceiro_id) REFERENCES parceiros (id),
                FOREIGN KEY (loja_id) REFERENCES lojas (id)
)
            ''')

            # Tabela de roles (permissões)
            self.execute('''
            CREATE TABLE IF NOT EXISTS roles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT UNIQUE NOT NULL
            )
            ''')

            # Tabela de usuários
            self.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role_id INTEGER NOT NULL,
                FOREIGN KEY (role_id) REFERENCES roles (id)
            )
            ''')

            # Inserir roles padrão se não existirem
            self.execute("SELECT COUNT(*) FROM roles")
            if self.fetchone()[0] == 0:
                self.executemany(
                    "INSERT INTO roles (nome) VALUES (?)",
                    [("Admin",), ("Operador",), ("Financeiro",), ("Visualizador",)]
                )

            # Criar usuário administrador padrão se não existir
            self.execute("SELECT COUNT(*) FROM users")
            if self.fetchone()[0] == 0:
                self.execute(
                    "INSERT INTO users (username, password, role_id) VALUES (?, ?, 1)",
                    ("admin", "admin")
                )

            # Commit das mudanças
            self.commit()
            self.logger.info("Estrutura do banco de dados configurada com sucesso")

        except sqlite3.Error as e:
            self.logger.error(f"Erro ao configurar o banco de dados: {str(e)}")
            raise