#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modelo de Usuário
-----------------
Classe para representar e gerenciar os dados de usuários do sistema.
"""

import logging
import sqlite3
from typing import Optional, Tuple

from werkzeug.security import check_password_hash, generate_password_hash


class Usuario:
    """Classe para representar um usuário do sistema."""

    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)

        self.id: Optional[int] = None
        self.username: Optional[str] = None
        self.password_hash: Optional[str] = None
        self.role_id: Optional[int] = None

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
            self.id, self.username, self.password_hash, self.role_id = row
            return True
        except Exception as exc:
            self.logger.error("Erro ao carregar usuário por ID: %s", exc)
            return False

    def salvar(self):
        """Insere ou atualiza o usuário no banco."""
        try:
            if not self.username or self.role_id is None:
                self.logger.error("Dados obrigatórios do usuário ausentes")
                return False

            self._ensure_password_hash()

            if not self.password_hash:
                self.logger.error("Senha do usuário não foi definida")
                return False

            if not self.id:
                self.db_manager.execute(
                    "INSERT INTO users (username, password, role_id) VALUES (?, ?, ?)",
                    (self.username, self.password_hash, self.role_id),
                )
                self.id = self.db_manager.last_insert_rowid()
            else:
                self.db_manager.execute(
                    "UPDATE users SET username=?, password=?, role_id=? WHERE id=?",
                    (self.username, self.password_hash, self.role_id, self.id),
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

    def set_password(self, password: str) -> None:
        """Define a senha do usuário utilizando hash seguro."""
        if password is None or not password.strip():
            raise ValueError("Senha não pode ser vazia")
        self.password_hash = generate_password_hash(password.strip())

    def verificar_senha(self, senha: str) -> bool:
        """Valida uma senha em relação ao hash armazenado."""
        if not senha:
            return False
        if not self.password_hash:
            return False
        if self._is_password_hashed(self.password_hash):
            return check_password_hash(self.password_hash, senha)
        return self.password_hash == senha

    def _ensure_password_hash(self) -> None:
        """Garante que a senha armazenada está em formato de hash."""
        if self.password_hash and not self._is_password_hashed(self.password_hash):
            self.password_hash = generate_password_hash(self.password_hash)

    @staticmethod
    def _is_password_hashed(valor: Optional[str]) -> bool:
        if not valor:
            return False
        partes = valor.split("$")
        return len(partes) >= 3 and ":" in partes[0]

    @classmethod
    def autenticar(cls, db_manager, username: str, senha: str) -> Tuple[bool, Optional["Usuario"]]:
        """Autentica um usuário utilizando hash de senha."""
        logger = logging.getLogger(__name__)
        try:
            db_manager.execute(
                "SELECT id, username, password, role_id FROM users WHERE username=?",
                (username,),
            )
            row = db_manager.fetchone()
            if not row:
                return False, None

            usuario_id, username_db, senha_armazenada, role_id = row
            senha_hashed = senha_armazenada
            autenticado = False

            if senha_armazenada and cls._is_password_hashed(senha_armazenada):
                autenticado = check_password_hash(senha_armazenada, senha)
            elif senha_armazenada == senha:
                autenticado = True
                senha_hashed = generate_password_hash(senha)
                db_manager.execute(
                    "UPDATE users SET password=? WHERE id=?",
                    (senha_hashed, usuario_id),
                )
                db_manager.commit()

            if not autenticado:
                return False, None

            usuario = cls(db_manager)
            usuario.id = usuario_id
            usuario.username = username_db
            usuario.password_hash = senha_hashed
            usuario.role_id = role_id
            logger.info("Usuário '%s' autenticado com sucesso", username_db)
            return True, usuario
        except Exception as exc:
            logger.error("Erro ao autenticar usuário '%s': %s", username, exc)
            return False, None

