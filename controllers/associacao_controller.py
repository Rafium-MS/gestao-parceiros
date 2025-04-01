#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Controlador de Associações
------------------------
Gerencia as operações relacionadas às associações entre parceiros e lojas,
conectando a interface com o modelo de dados.
"""

import logging
import datetime
from models.associacao import Associacao
from controllers.parceiro_controller import ParceiroController
from controllers.loja_controller import LojaController


class AssociacaoController:
    """Controlador para gerenciamento de associações."""

    def __init__(self, db_manager):
        """
        Inicializa o controlador de associações.

        Args:
            db_manager (DatabaseManager): Instância do gerenciador de banco de dados.
        """
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)

        # Controladores auxiliares para obter dados de parceiros e lojas
        self.parceiro_controller = ParceiroController(db_manager)
        self.loja_controller = LojaController(db_manager)

    def adicionar_associacao(self, dados):
        """
        Adiciona uma nova associação entre parceiro e loja.

        Args:
            dados (dict): Dicionário com os dados da associação.
                Deve conter: parceiro_id, loja_id, status
                Pode conter: observacao

        Returns:
            tuple: (bool, str) Indica se a operação foi bem-sucedida e mensagem.
        """
        try:
            # Validar dados obrigatórios
            if not dados.get('parceiro_id'):
                return False, "Parceiro é obrigatório!"

            if not dados.get('loja_id'):
                return False, "Loja é obrigatória!"

            # Verificar se já existe uma associação entre o parceiro e a loja
            self.db_manager.execute(
                """
                SELECT id FROM associacoes 
                WHERE parceiro_id = ? AND loja_id = ?
                """,
                (dados.get('parceiro_id'), dados.get('loja_id'))
            )
            existing = self.db_manager.fetchone()

            if existing:
                return False, "Já existe uma associação entre este parceiro e esta loja!"

            # Obter nomes de parceiro e loja para log e mensagens
            parceiro_nome = self._obter_nome_parceiro(dados.get('parceiro_id'))
            loja_nome = self._obter_nome_loja(dados.get('loja_id'))

            # Criar e salvar associação
            associacao = Associacao(self.db_manager)
            associacao.parceiro_id = dados.get('parceiro_id')
            associacao.loja_id = dados.get('loja_id')
            associacao.status = dados.get('status', 'Ativo')
            associacao.observacao = dados.get('observacao', '')
            associacao.data_associacao = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if associacao.salvar():
                self.logger.info(f"Associação criada entre parceiro '{parceiro_nome}' e loja '{loja_nome}'.")
                return True, f"Associação entre '{parceiro_nome}' e '{loja_nome}' criada com sucesso!"
            else:
                return False, "Erro ao salvar associação. Verifique os dados e tente novamente."

        except Exception as e:
            self.logger.error(f"Erro ao adicionar associação: {str(e)}")
            return False, f"Erro ao adicionar associação: {str(e)}"

    def editar_associacao(self, associacao_id, dados):
        """
        Edita uma associação existente.

        Args:
            associacao_id (int): ID da associação a ser editada.
            dados (dict): Dicionário com os novos dados da associação.
                Pode conter: parceiro_id, loja_id, status, observacao

        Returns:
            tuple: (bool, str) Indica se a operação foi bem-sucedida e mensagem.
        """
        try:
            # Validar dados obrigatórios
            if not dados.get('parceiro_id'):
                return False, "Parceiro é obrigatório!"

            if not dados.get('loja_id'):
                return False, "Loja é obrigatória!"

            # Carregar associação existente
            associacao = Associacao(self.db_manager)
            if not associacao.carregar_por_id(associacao_id):
                return False, f"Associação com ID {associacao_id} não encontrada."

            # Verificar se a nova combinação já existe (se parceiro_id ou loja_id foram alterados)
            if (associacao.parceiro_id != dados.get('parceiro_id') or
                    associacao.loja_id != dados.get('loja_id')):

                self.db_manager.execute(
                    """
                    SELECT id FROM associacoes 
                    WHERE parceiro_id = ? AND loja_id = ? AND id != ?
                    """,
                    (dados.get('parceiro_id'), dados.get('loja_id'), associacao_id)
                )
                existing = self.db_manager.fetchone()

                if existing:
                    return False, "Já existe uma associação entre este parceiro e esta loja!"

            # Obter nomes de parceiro e loja para log e mensagens
            parceiro_nome = self._obter_nome_parceiro(dados.get('parceiro_id'))
            loja_nome = self._obter_nome_loja(dados.get('loja_id'))

            # Atualizar dados
            associacao.parceiro_id = dados.get('parceiro_id')
            associacao.loja_id = dados.get('loja_id')
            associacao.status = dados.get('status', associacao.status)
            associacao.observacao = dados.get('observacao', associacao.observacao)

            if associacao.salvar():
                self.logger.info(
                    f"Associação entre parceiro '{parceiro_nome}' e loja '{loja_nome}' (ID: {associacao_id}) atualizada.")
                return True, f"Associação entre '{parceiro_nome}' e '{loja_nome}' atualizada com sucesso!"
            else:
                return False, "Erro ao atualizar associação. Verifique os dados e tente novamente."

        except Exception as e:
            self.logger.error(f"Erro ao editar associação: {str(e)}")
            return False, f"Erro ao editar associação: {str(e)}"

    def excluir_associacao(self, associacao_id):
        """
        Exclui uma associação.

        Args:
            associacao_id (int): ID da associação a ser excluída.

        Returns:
            tuple: (bool, str) Indica se a operação foi bem-sucedida e mensagem.
        """
        try:
            # Carregar associação
            associacao = Associacao(self.db_manager)
            if not associacao.carregar_por_id(associacao_id):
                return False, f"Associação com ID {associacao_id} não encontrada."

            # Obter nomes de parceiro e loja para log e mensagens
            parceiro_nome = self._obter_nome_parceiro(associacao.parceiro_id)
            loja_nome = self._obter_nome_loja(associacao.loja_id)

            # Verificar se existem comprovantes vinculados a esta associação
            self.db_manager.execute(
                """
                SELECT COUNT(*) FROM comprovantes 
                WHERE parceiro_id = ? AND loja_id = ?
                """,
                (associacao.parceiro_id, associacao.loja_id)
            )
            count = self.db_manager.fetchone()[0]

            if count > 0:
                self.logger.warning(f"Tentativa de excluir associação com {count} comprovantes vinculados.")
                return False, f"Não é possível excluir esta associação pois existem {count} comprovantes vinculados a ela."

            # Excluir associação
            if associacao.excluir():
                self.logger.info(
                    f"Associação entre parceiro '{parceiro_nome}' e loja '{loja_nome}' (ID: {associacao_id}) excluída.")
                return True, f"Associação entre '{parceiro_nome}' e '{loja_nome}' excluída com sucesso!"
            else:
                return False, "Erro ao excluir associação. Tente novamente."

        except Exception as e:
            self.logger.error(f"Erro ao excluir associação: {str(e)}")
            return False, f"Erro ao excluir associação: {str(e)}"

    def listar_associacoes(self):
        """
        Lista todas as associações cadastradas.

        Returns:
            list: Lista de tuplas contendo os dados das associações.
        """
        try:
            return Associacao.listar_todas(self.db_manager)
        except Exception as e:
            self.logger.error(f"Erro ao listar associações: {str(e)}")
            return []

    def pesquisar_associacoes(self, termo):
        """
        Pesquisa associações por termo.

        Args:
            termo (str): Termo a ser pesquisado.

        Returns:
            list: Lista de tuplas contendo os dados das associações encontradas.
        """
        try:
            return Associacao.pesquisar(self.db_manager, termo)
        except Exception as e:
            self.logger.error(f"Erro ao pesquisar associações: {str(e)}")
            return []

    def filtrar_associacoes(self, parceiro_id=None, loja_id=None, status=None):
        """
        Filtra associações por parceiro, loja e/ou status.

        Args:
            parceiro_id (int, optional): ID do parceiro para filtrar.
            loja_id (int, optional): ID da loja para filtrar.
            status (str, optional): Status para filtrar.

        Returns:
            list: Lista de tuplas contendo os dados das associações filtradas.
        """
        try:
            return Associacao.filtrar(self.db_manager, parceiro_id, loja_id, status)
        except Exception as e:
            self.logger.error(f"Erro ao filtrar associações: {str(e)}")
            return []

    def obter_associacao(self, associacao_id):
        """
        Obtém os dados de uma associação específica.

        Args:
            associacao_id (int): ID da associação.

        Returns:
            dict: Dicionário com os dados da associação ou None se não encontrada.
        """
        try:
            associacao = Associacao(self.db_manager)
            if associacao.carregar_por_id(associacao_id):
                return associacao.to_dict()
            return None
        except Exception as e:
            self.logger.error(f"Erro ao obter associação: {str(e)}")
            return None

    def obter_parceiros_combobox(self):
        """
        Obtém a lista de parceiros para preencher combobox.

        Returns:
            dict: Dicionário onde as chaves são os nomes dos parceiros e os valores são os IDs.
        """
        try:
            return self.parceiro_controller.obter_parceiros_combobox()
        except Exception as e:
            self.logger.error(f"Erro ao obter lista de parceiros: {str(e)}")
            return {}

    def obter_lojas_combobox(self):
        """
        Obtém a lista de lojas para preencher combobox.

        Returns:
            dict: Dicionário onde as chaves são os nomes das lojas e os valores são os IDs.
        """
        try:
            return self.loja_controller.obter_lojas_combobox()
        except Exception as e:
            self.logger.error(f"Erro ao obter lista de lojas: {str(e)}")
            return {}

    def obter_associacoes_por_parceiro(self, parceiro_id):
        """
        Obtém as associações de um parceiro específico.

        Args:
            parceiro_id (int): ID do parceiro.

        Returns:
            list: Lista de tuplas contendo os dados das associações do parceiro.
        """
        try:
            return Associacao.filtrar(self.db_manager, parceiro_id=parceiro_id)
        except Exception as e:
            self.logger.error(f"Erro ao obter associações por parceiro: {str(e)}")
            return []

    def obter_associacoes_por_loja(self, loja_id):
        """
        Obtém as associações de uma loja específica.

        Args:
            loja_id (int): ID da loja.

        Returns:
            list: Lista de tuplas contendo os dados das associações da loja.
        """
        try:
            return Associacao.filtrar(self.db_manager, loja_id=loja_id)
        except Exception as e:
            self.logger.error(f"Erro ao obter associações por loja: {str(e)}")
            return []

    def verificar_associacao(self, parceiro_id, loja_id):
        """
        Verifica se existe uma associação ativa entre parceiro e loja.

        Args:
            parceiro_id (int): ID do parceiro.
            loja_id (int): ID da loja.

        Returns:
            bool: True se existe uma associação ativa, False caso contrário.
        """
        try:
            self.db_manager.execute(
                """
                SELECT id FROM associacoes 
                WHERE parceiro_id = ? AND loja_id = ? AND status = 'Ativo'
                """,
                (parceiro_id, loja_id)
            )
            return self.db_manager.fetchone() is not None
        except Exception as e:
            self.logger.error(f"Erro ao verificar associação: {str(e)}")
            return False

    def _obter_nome_parceiro(self, parceiro_id):
        """
        Obtém o nome de um parceiro pelo ID.

        Args:
            parceiro_id (int): ID do parceiro.

        Returns:
            str: Nome do parceiro ou ID se não encontrado.
        """
        try:
            parceiro = self.parceiro_controller.obter_parceiro(parceiro_id)
            return parceiro['nome'] if parceiro else f"ID: {parceiro_id}"
        except Exception as e:
            self.logger.error(f"Erro ao obter nome do parceiro: {str(e)}")
            return f"ID: {parceiro_id}"

    def _obter_nome_loja(self, loja_id):
        """
        Obtém o nome de uma loja pelo ID.

        Args:
            loja_id (int): ID da loja.

        Returns:
            str: Nome da loja ou ID se não encontrada.
        """
        try:
            loja = self.loja_controller.obter_loja(loja_id)
            return loja['nome'] if loja else f"ID: {loja_id}"
        except Exception as e:
            self.logger.error(f"Erro ao obter nome da loja: {str(e)}")
            return f"ID: {loja_id}"