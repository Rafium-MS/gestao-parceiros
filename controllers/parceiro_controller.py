#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Controlador de Parceiros
-----------------------
Gerencia as operações relacionadas aos parceiros, conectando a interface com o modelo de dados.
"""

import logging
from tkinter import messagebox
from models.parceiro import Parceiro
from utils.validators import validar_cpf, validar_email


class ParceiroController:
    """Controlador para gerenciamento de parceiros."""

    def __init__(self, db_manager):
        """
        Inicializa o controlador de parceiros.

        Args:
            db_manager (DatabaseManager): Instância do gerenciador de banco de dados.
        """
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)

    def adicionar_parceiro(self, dados):
        """
        Adiciona um novo parceiro.

        Args:
            dados (dict): Dicionário com os dados do parceiro.
                Deve conter: nome, cpf, telefone, email, endereco

        Returns:
            bool: True se o parceiro foi adicionado com sucesso, False caso contrário.
            str: Mensagem de erro, se houver, ou mensagem de sucesso.
        """
        try:
            # Validar dados
            if not dados.get('nome'):
                return False, "Nome é obrigatório!"

            cpf = dados.get('cpf')
            if cpf and not validar_cpf(cpf):
                return False, "CPF inválido!"

            email = dados.get('email')
            if email and not validar_email(email):
                return False, "E-mail inválido!"

            # Criar e salvar parceiro
            parceiro = Parceiro(self.db_manager)
            parceiro.nome = dados.get('nome')
            parceiro.cpf = cpf
            parceiro.telefone = dados.get('telefone')
            parceiro.email = email
            parceiro.endereco = dados.get('endereco')

            if parceiro.salvar():
                self.logger.info(f"Parceiro '{parceiro.nome}' adicionado com sucesso.")
                return True, f"Parceiro '{parceiro.nome}' adicionado com sucesso!"
            else:
                return False, "Erro ao salvar parceiro. Verifique os dados e tente novamente."

        except ValueError as e:
            self.logger.error(f"Erro de validação ao adicionar parceiro: {str(e)}")
            return False, str(e)

        except Exception as e:
            self.logger.error(f"Erro inesperado ao adicionar parceiro: {str(e)}")
            return False, f"Erro ao adicionar parceiro: {str(e)}"

    def editar_parceiro(self, parceiro_id, dados):
        """
        Edita um parceiro existente.

        Args:
            parceiro_id (int): ID do parceiro a ser editado.
            dados (dict): Dicionário com os novos dados do parceiro.
                Pode conter: nome, cpf, telefone, email, endereco

        Returns:
            bool: True se o parceiro foi editado com sucesso, False caso contrário.
            str: Mensagem de erro, se houver, ou mensagem de sucesso.
        """
        try:
            # Validar dados
            if not dados.get('nome'):
                return False, "Nome é obrigatório!"

            cpf = dados.get('cpf')
            if cpf and not validar_cpf(cpf):
                return False, "CPF inválido!"

            email = dados.get('email')
            if email and not validar_email(email):
                return False, "E-mail inválido!"

            # Carregar parceiro existente
            parceiro = Parceiro(self.db_manager)
            if not parceiro.carregar_por_id(parceiro_id):
                return False, f"Parceiro com ID {parceiro_id} não encontrado."

            # Atualizar dados
            parceiro.nome = dados.get('nome')
            parceiro.cpf = cpf
            parceiro.telefone = dados.get('telefone')
            parceiro.email = email
            parceiro.endereco = dados.get('endereco')

            if parceiro.salvar():
                self.logger.info(f"Parceiro '{parceiro.nome}' (ID: {parceiro_id}) atualizado com sucesso.")
                return True, f"Parceiro '{parceiro.nome}' atualizado com sucesso!"
            else:
                return False, "Erro ao atualizar parceiro. Verifique os dados e tente novamente."

        except ValueError as e:
            self.logger.error(f"Erro de validação ao editar parceiro: {str(e)}")
            return False, str(e)

        except Exception as e:
            self.logger.error(f"Erro inesperado ao editar parceiro: {str(e)}")
            return False, f"Erro ao editar parceiro: {str(e)}"

    def excluir_parceiro(self, parceiro_id):
        """
        Exclui um parceiro.

        Args:
            parceiro_id (int): ID do parceiro a ser excluído.

        Returns:
            bool: True se o parceiro foi excluído com sucesso, False caso contrário.
            str: Mensagem de erro, se houver, ou mensagem de sucesso.
        """
        try:
            # Carregar parceiro
            parceiro = Parceiro(self.db_manager)
            if not parceiro.carregar_por_id(parceiro_id):
                return False, f"Parceiro com ID {parceiro_id} não encontrado."

            nome_parceiro = parceiro.nome

            # Verificar associações e comprovantes
            self.db_manager.execute(
                "SELECT COUNT(*) FROM associacoes WHERE parceiro_id = ?",
                (parceiro_id,)
            )
            count_associacoes = self.db_manager.fetchone()[0]

            self.db_manager.execute(
                "SELECT COUNT(*) FROM comprovantes WHERE parceiro_id = ?",
                (parceiro_id,)
            )
            count_comprovantes = self.db_manager.fetchone()[0]

            # Confirmar exclusão se existirem registros relacionados
            if count_associacoes > 0 or count_comprovantes > 0:
                mensagem = f"O parceiro '{nome_parceiro}' possui:\n"
                if count_associacoes > 0:
                    mensagem += f"- {count_associacoes} associação(ões) com lojas\n"
                if count_comprovantes > 0:
                    mensagem += f"- {count_comprovantes} comprovante(s) de entrega\n"
                mensagem += "\nTodos esses registros serão excluídos junto com o parceiro. Deseja continuar?"

                confirmacao = messagebox.askyesno("Confirmar Exclusão", mensagem)
                if not confirmacao:
                    return False, "Exclusão cancelada pelo usuário."

            # Excluir parceiro e registros relacionados
            if parceiro.excluir():
                self.logger.info(f"Parceiro '{nome_parceiro}' (ID: {parceiro_id}) excluído com sucesso.")
                return True, f"Parceiro '{nome_parceiro}' excluído com sucesso!"
            else:
                return False, "Erro ao excluir parceiro. Tente novamente."

        except Exception as e:
            self.logger.error(f"Erro ao excluir parceiro: {str(e)}")
            return False, f"Erro ao excluir parceiro: {str(e)}"

    def listar_parceiros(self):
        """
        Lista todos os parceiros cadastrados.

        Returns:
            list: Lista de tuplas contendo os dados dos parceiros.
        """
        try:
            return Parceiro.listar_todos(self.db_manager)
        except Exception as e:
            self.logger.error(f"Erro ao listar parceiros: {str(e)}")
            return []

    def pesquisar_parceiros(self, termo):
        """
        Pesquisa parceiros por termo.

        Args:
            termo (str): Termo a ser pesquisado.

        Returns:
            list: Lista de tuplas contendo os dados dos parceiros encontrados.
        """
        try:
            return Parceiro.pesquisar(self.db_manager, termo)
        except Exception as e:
            self.logger.error(f"Erro ao pesquisar parceiros: {str(e)}")
            return []

    def obter_parceiro(self, parceiro_id):
        """
        Obtém os dados de um parceiro específico.

        Args:
            parceiro_id (int): ID do parceiro.

        Returns:
            dict: Dicionário com os dados do parceiro ou None se não encontrado.
        """
        try:
            parceiro = Parceiro(self.db_manager)
            if parceiro.carregar_por_id(parceiro_id):
                return parceiro.to_dict()
            return None
        except Exception as e:
            self.logger.error(f"Erro ao obter parceiro: {str(e)}")
            return None

    def obter_parceiros_combobox(self):
        """
        Obtém os parceiros para preencher um combobox.

        Returns:
            dict: Dicionário onde as chaves são os nomes dos parceiros e os valores são os IDs.
        """
        try:
            self.db_manager.execute("SELECT id, nome FROM parceiros ORDER BY nome")
            parceiros = self.db_manager.fetchall()
            return {p[1]: p[0] for p in parceiros}
        except Exception as e:
            self.logger.error(f"Erro ao obter parceiros para combobox: {str(e)}")
            return {}