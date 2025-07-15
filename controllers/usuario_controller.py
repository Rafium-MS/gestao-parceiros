#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Controlador de Usuários
----------------------
Gerencia operações relacionadas aos usuários do sistema.
"""

import logging
from models.usuario import Usuario


class UsuarioController:
    """Controlador para gerenciamento de usuários."""

    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)

    def listar_usuarios(self):
        return Usuario.listar_todos(self.db_manager)

    def listar_roles(self):
        return Usuario.listar_roles(self.db_manager)

    def adicionar_usuario(self, dados):
        try:
            if not dados.get("username") or not dados.get("password") or not dados.get("role_id"):
                return False, "Preencha usuário, senha e perfil."
            usuario = Usuario(self.db_manager)
            usuario.username = dados["username"].strip()
            usuario.password = dados["password"].strip()
            usuario.role_id = dados["role_id"]
            if usuario.salvar():
                return True, "Usuário adicionado com sucesso."
            return False, "Erro ao salvar usuário."
        except Exception as exc:
            self.logger.error("Erro ao adicionar usuário: %s", exc)
            return False, str(exc)

    def editar_usuario(self, usuario_id, dados):
        try:
            usuario = Usuario(self.db_manager)
            if not usuario.carregar_por_id(usuario_id):
                return False, "Usuário não encontrado."
            usuario.username = dados.get("username", usuario.username).strip()
            usuario.password = dados.get("password", usuario.password).strip()
            usuario.role_id = dados.get("role_id", usuario.role_id)
            if usuario.salvar():
                return True, "Usuário atualizado com sucesso."
            return False, "Erro ao atualizar usuário."
        except Exception as exc:
            self.logger.error("Erro ao editar usuário: %s", exc)
            return False, str(exc)

    def excluir_usuario(self, usuario_id):
        try:
            usuario = Usuario(self.db_manager)
            if not usuario.carregar_por_id(usuario_id):
                return False, "Usuário não encontrado."
            if usuario.excluir():
                return True, "Usuário excluído com sucesso."
            return False, "Erro ao excluir usuário."
        except Exception as exc:
            self.logger.error("Erro ao excluir usuário: %s", exc)
            return False, str(exc)