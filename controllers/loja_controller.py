#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Controlador de Lojas
-----------------------
Gerencia as operações relacionadas às lojas, conectando a interface com o modelo de dados.
"""

import logging
from tkinter import messagebox
from models.loja import Loja
from utils.validators import validar_cnpj, validar_email


class LojaController:
    """Controlador para gerenciamento de lojas."""

    def __init__(self, db_manager):
        """
        Inicializa o controlador de lojas.

        Args:
            db_manager (DatabaseManager): Instância do gerenciador de banco de dados.
        """
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)

    def adicionar_loja(self, dados):
        """
        Adiciona uma nova loja.

        Args:
            dados (dict): Dicionário com os dados da loja.
                Deve conter: nome, cnpj, telefone, email, endereco, contato

        Returns:
            bool: True se a loja foi adicionada com sucesso, False caso contrário.
            str: Mensagem de erro, se houver, ou mensagem de sucesso.
        """
        try:
            # Validar dados
            if not dados.get('nome'):
                return False, "Nome é obrigatório!"

            cnpj = dados.get('cnpj')
            if cnpj and not validar_cnpj(cnpj):
                return False, "CNPJ inválido!"

            email = dados.get('email')
            if email and not validar_email(email):
                return False, "E-mail inválido!"

            # Criar e salvar loja
            loja = Loja(self.db_manager)
            loja.nome = dados.get('nome')
            loja.cnpj = cnpj
            loja.telefone = dados.get('telefone')
            loja.email = email
            loja.endereco = dados.get('endereco')
            loja.contato = dados.get('contato')

            if loja.salvar():
                self.logger.info(f"Loja '{loja.nome}' adicionada com sucesso.")
                return True, f"Loja '{loja.nome}' adicionada com sucesso!"
            else:
                return False, "Erro ao salvar loja. Verifique os dados e tente novamente."

        except ValueError as e:
            self.logger.error(f"Erro de validação ao adicionar loja: {str(e)}")
            return False, str(e)

        except Exception as e:
            self.logger.error(f"Erro inesperado ao adicionar loja: {str(e)}")
            return False, f"Erro ao adicionar loja: {str(e)}"

    def editar_loja(self, loja_id, dados):
        """
        Edita uma loja existente.

        Args:
            loja_id (int): ID da loja a ser editada.
            dados (dict): Dicionário com os novos dados da loja.
                Pode conter: nome, cnpj, telefone, email, endereco, contato

        Returns:
            bool: True se a loja foi editada com sucesso, False caso contrário.
            str: Mensagem de erro, se houver, ou mensagem de sucesso.
        """
        try:
            # Validar dados
            if not dados.get('nome'):
                return False, "Nome é obrigatório!"

            cnpj = dados.get('cnpj')
            if cnpj and not validar_cnpj(cnpj):
                return False, "CNPJ inválido!"

            email = dados.get('email')
            if email and not validar_email(email):
                return False, "E-mail inválido!"

            # Carregar loja existente
            loja = Loja(self.db_manager)
            if not loja.carregar_por_id(loja_id):
                return False, f"Loja com ID {loja_id} não encontrada."

            # Atualizar dados
            loja.nome = dados.get('nome')
            loja.cnpj = cnpj
            loja.telefone = dados.get('telefone')
            loja.email = email
            loja.endereco = dados.get('endereco')
            loja.contato = dados.get('contato')

            if loja.salvar():
                self.logger.info(f"Loja '{loja.nome}' (ID: {loja_id}) atualizada com sucesso.")
                return True, f"Loja '{loja.nome}' atualizada com sucesso!"
            else:
                return False, "Erro ao atualizar loja. Verifique os dados e tente novamente."

        except ValueError as e:
            self.logger.error(f"Erro de validação ao editar loja: {str(e)}")
            return False, str(e)

        except Exception as e:
            self.logger.error(f"Erro inesperado ao editar loja: {str(e)}")
            return False, f"Erro ao editar loja: {str(e)}"

    def excluir_loja(self, loja_id):
        """
        Exclui uma loja.

        Args:
            loja_id (int): ID da loja a ser excluída.

        Returns:
            bool: True se a loja foi excluída com sucesso, False caso contrário.
            str: Mensagem de erro, se houver, ou mensagem de sucesso.
        """
        try:
            # Carregar loja
            loja = Loja(self.db_manager)
            if not loja.carregar_por_id(loja_id):
                return False, f"Loja com ID {loja_id} não encontrada."

            nome_loja = loja.nome

            # Verificar associações e comprovantes
            self.db_manager.execute(
                "SELECT COUNT(*) FROM associacoes WHERE loja_id = ?",
                (loja_id,)
            )
            count_associacoes = self.db_manager.fetchone()[0]

            self.db_manager.execute(
                "SELECT COUNT(*) FROM comprovantes WHERE loja_id = ?",
                (loja_id,)
            )
            count_comprovantes = self.db_manager.fetchone()[0]

            # Confirmar exclusão se existirem registros relacionados
            if count_associacoes > 0 or count_comprovantes > 0:
                mensagem = f"A loja '{nome_loja}' possui:\n"
                if count_associacoes > 0:
                    mensagem += f"- {count_associacoes} associação(ões) com parceiros\n"
                if count_comprovantes > 0:
                    mensagem += f"- {count_comprovantes} comprovante(s) de entrega\n"
                mensagem += "\nTodos esses registros serão excluídos junto com a loja. Deseja continuar?"

                confirmacao = messagebox.askyesno("Confirmar Exclusão", mensagem)
                if not confirmacao:
                    return False, "Exclusão cancelada pelo usuário."

            # Excluir loja e registros relacionados
            if loja.excluir():
                self.logger.info(f"Loja '{nome_loja}' (ID: {loja_id}) excluída com sucesso.")
                return True, f"Loja '{nome_loja}' excluída com sucesso!"
            else:
                return False, "Erro ao excluir loja. Tente novamente."

        except Exception as e:
            self.logger.error(f"Erro ao excluir loja: {str(e)}")
            return False, f"Erro ao excluir loja: {str(e)}"

    def listar_lojas(self):
        """
        Lista todas as lojas cadastradas.

        Returns:
            list: Lista de tuplas contendo os dados das lojas.
        """
        try:
            return Loja.listar_todas(self.db_manager)
        except Exception as e:
            self.logger.error(f"Erro ao listar lojas: {str(e)}")
            return []

    def pesquisar_lojas(self, termo):
        """
        Pesquisa lojas por termo.

        Args:
            termo (str): Termo a ser pesquisado.

        Returns:
            list: Lista de tuplas contendo os dados das lojas encontradas.
        """
        try:
            return Loja.pesquisar(self.db_manager, termo)
        except Exception as e:
            self.logger.error(f"Erro ao pesquisar lojas: {str(e)}")
            return []

    def obter_loja(self, loja_id):
        """
        Obtém os dados de uma loja específica.

        Args:
            loja_id (int): ID da loja.

        Returns:
            dict: Dicionário com os dados da loja ou None se não encontrada.
        """
        try:
            loja = Loja(self.db_manager)
            if loja.carregar_por_id(loja_id):
                return loja.to_dict()
            return None
        except Exception as e:
            self.logger.error(f"Erro ao obter loja: {str(e)}")
            return None

    def obter_lojas_combobox(self):
        """
        Obtém as lojas para preencher um combobox.

        Returns:
            dict: Dicionário onde as chaves são os nomes das lojas e os valores são os IDs.
        """
        try:
            self.db_manager.execute("SELECT id, nome FROM lojas ORDER BY nome")
            lojas = self.db_manager.fetchall()
            return {l[1]: l[0] for l in lojas}
        except Exception as e:
            self.logger.error(f"Erro ao obter lojas para combobox: {str(e)}")
            return {}

    def obter_lojas_por_cidade(self, cidade):
        """Obtém lojas filtradas pela cidade."""
        try:
            self.db_manager.execute(
                "SELECT id, nome FROM lojas WHERE cidade = ? ORDER BY nome",
                (cidade,),
            )
            resultados = self.db_manager.fetchall()
            return [{"id": row[0], "nome": row[1]} for row in resultados]
        except Exception as e:
            self.logger.error(
                f"Erro ao obter lojas da cidade {cidade}: {str(e)}"
            )
            return []