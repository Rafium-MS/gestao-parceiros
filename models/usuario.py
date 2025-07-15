#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modelo de Usuário
-----------------
Classe para representar e gerenciar os dados de usuários do sistema.
"""

import logging
import sqlite3


class Usuario:
    """Classe para representar um usuário do sistema."""

    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)

        self.id = None
        self.username = None
        self.password = None
        self.role_id = None

    def carregar_por_id(self, usuario_id):
        """Carrega um usuário pelo ID."""
        try:
            self.db_manager.execute(
                "SELECT id, username, password, role_id FROM users WHERE id = ?",
                (usuario_id,),
            )
            row = self.db_manager.fetchone()
            if not row:
                return False
            self.id, self.username, self.password, self.role_id = row
            return True
        except Exception as exc:
            self.logger.error("Erro ao carregar usuário por ID: %s", exc)
            return False

    def salvar(self):
        """Insere ou atualiza o usuário no banco."""
        try:
            if not self.username or not self.password or not self.role_id:
                self.logger.error("Dados obrigatórios do usuário ausentes")
                return False

            if not self.id:
                self.db_manager.execute(
                    "INSERT INTO users (username, password, role_id) VALUES (?, ?, ?)",
                    (self.username, self.password, self.role_id),
                )
                self.id = self.db_manager.last_insert_rowid()
            else:
                self.db_manager.execute(
                    "UPDATE users SET username=?, password=?, role_id=? WHERE id=?",
                    (self.username, self.password, self.role_id, self.id),
                )
            self.db_manager.commit()
            return True
        except sqlite3.IntegrityError as exc:
            self.logger.error("Erro de integridade ao salvar usuário: %s", exc)
            return False
        except Exception as exc:
            self.logger.error("Erro ao salvar usuário: %s", exc)
            return False

    def excluir(self):
        """Exclui o usuário do banco de dados."""
        if not self.id:
            return False
        try:
            self.db_manager.execute("DELETE FROM users WHERE id = ?", (self.id,))
            self.db_manager.commit()
            return True
        except Exception as exc:
            self.logger.error("Erro ao excluir usuário: %s", exc)
            return False

    @classmethod
    def listar_todos(cls, db_manager):
        """Retorna todos os usuários com seus papéis."""
        try:
            db_manager.execute(
                """
                SELECT u.id, u.username, r.nome
                FROM users u
                JOIN roles r ON u.role_id = r.id
                ORDER BY u.username
                """
            )
            return db_manager.fetchall()
        except Exception as exc:
            logging.getLogger(__name__).error("Erro ao listar usuários: %s", exc)
            return []

    @classmethod
    def listar_roles(cls, db_manager):
        """Retorna todos os papéis cadastrados."""
        try:
            db_manager.execute("SELECT id, nome FROM roles ORDER BY nome")
            return db_manager.fetchall()
        except Exception as exc:
            logging.getLogger(__name__).error("Erro ao listar roles: %s", exc)
            return []