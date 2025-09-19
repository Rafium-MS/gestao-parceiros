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
            username = (dados.get("username") or "").strip()
            role_id = dados.get("role_id")
            password = dados.get("password")

            if not username or role_id is None:
                return False, "Preencha usuário e perfil."

            password = (password or "").strip()
            if not password:
                return False, "Informe uma senha válida."

            usuario = Usuario(self.db_manager)
            usuario.username = username
            usuario.role_id = role_id
            usuario.set_password(password)
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

            novo_username = dados.get("username")
            if novo_username is not None:
                novo_username = novo_username.strip()
                if novo_username:
                    usuario.username = novo_username

            novo_role = dados.get("role_id")
            if novo_role is not None:
                usuario.role_id = novo_role

            nova_senha = dados.get("password")
            if nova_senha is not None:
                nova_senha = nova_senha.strip()
                if nova_senha:
                    usuario.set_password(nova_senha)
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