#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Controlador de Comprovantes
--------------------------
Gerencia as operações relacionadas aos comprovantes de entrega, conectando a interface com o modelo de dados.
"""

import os
import logging
import datetime
from models.comprovante import Comprovante


class ComprovanteController:
    """Controlador para gerenciamento de comprovantes de entrega."""

    def __init__(self, db_manager):
        """
        Inicializa o controlador de comprovantes.

        Args:
            db_manager (DatabaseManager): Instância do gerenciador de banco de dados.
        """
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)

    def adicionar_comprovante(self, dados):
        """
        Adiciona um novo comprovante de entrega.

        Args:
            dados (dict): Dicionário com os dados do comprovante.
                Deve conter: parceiro_id, loja_id, data_entrega, arquivo, observacoes

        Returns:
            bool: True se o comprovante foi adicionado com sucesso, False caso contrário.
            str: Mensagem de erro, se houver, ou mensagem de sucesso.
        """
        try:
            # Validar dados
            if not dados.get('parceiro_id'):
                return False, "Parceiro é obrigatório!"

            if not dados.get('loja_id'):
                return False, "Loja é obrigatória!"

            if not dados.get('data_entrega'):
                return False, "Data de entrega é obrigatória!"

            if not dados.get('arquivo'):
                return False, "Arquivo de comprovante é obrigatório!"

            # Verificar se o arquivo existe
            arquivo = dados.get('arquivo')
            comprovantes_dir = self._obter_diretorio_comprovantes()
            caminho_arquivo = os.path.join(comprovantes_dir, arquivo)

            if not os.path.exists(caminho_arquivo):
                return False, f"Arquivo '{arquivo}' não encontrado no diretório de comprovantes!"

            # Verificar se a associação entre parceiro e loja existe
            self.db_manager.execute(
                """
                SELECT COUNT(*) FROM associacoes 
                WHERE parceiro_id = ? AND loja_id = ? AND status = 'Ativo'
                """,
                (dados.get('parceiro_id'), dados.get('loja_id'))
            )

            count = self.db_manager.fetchone()[0]
            if count == 0:
                # Verificar se existe, mas está inativo
                self.db_manager.execute(
                    """
                    SELECT COUNT(*) FROM associacoes 
                    WHERE parceiro_id = ? AND loja_id = ?
                    """,
                    (dados.get('parceiro_id'), dados.get('loja_id'))
                )
                count_inativo = self.db_manager.fetchone()[0]

                if count_inativo > 0:
                    return False, "Associação entre parceiro e loja existe, mas está inativa ou pendente!"
                else:
                    return False, "Não existe associação entre este parceiro e esta loja!"

            # Criar e salvar comprovante
            comprovante = Comprovante(self.db_manager)
            comprovante.parceiro_id = dados.get('parceiro_id')
            comprovante.loja_id = dados.get('loja_id')
            comprovante.data_entrega = dados.get('data_entrega')
            comprovante.arquivo = dados.get('arquivo')
            comprovante.observacoes = dados.get('observacoes')

            if comprovante.salvar():
                nome_parceiro = self._obter_nome_parceiro(dados.get('parceiro_id'))
                nome_loja = self._obter_nome_loja(dados.get('loja_id'))
                self.logger.info(
                    f"Comprovante de entrega para '{nome_parceiro}' na loja '{nome_loja}' adicionado com sucesso.")
                return True, f"Comprovante de entrega adicionado com sucesso!"
            else:
                return False, "Erro ao salvar comprovante. Verifique os dados e tente novamente."

        except Exception as e:
            self.logger.error(f"Erro inesperado ao adicionar comprovante: {str(e)}")
            return False, f"Erro ao adicionar comprovante: {str(e)}"

    def editar_comprovante(self, comprovante_id, dados):
        """
        Edita um comprovante existente.

        Args:
            comprovante_id (int): ID do comprovante a ser editado.
            dados (dict): Dicionário com os novos dados do comprovante.
                Pode conter: parceiro_id, loja_id, data_entrega, arquivo, observacoes

        Returns:
            bool: True se o comprovante foi editado com sucesso, False caso contrário.
            str: Mensagem de erro, se houver, ou mensagem de sucesso.
        """
        try:
            # Validar dados
            if not dados.get('parceiro_id'):
                return False, "Parceiro é obrigatório!"

            if not dados.get('loja_id'):
                return False, "Loja é obrigatória!"

            if not dados.get('data_entrega'):
                return False, "Data de entrega é obrigatória!"

            # Verificar se a associação entre parceiro e loja existe
            if dados.get('parceiro_id') and dados.get('loja_id'):
                self.db_manager.execute(
                    """
                    SELECT COUNT(*) FROM associacoes 
                    WHERE parceiro_id = ? AND loja_id = ? AND status = 'Ativo'
                    """,
                    (dados.get('parceiro_id'), dados.get('loja_id'))
                )

                count = self.db_manager.fetchone()[0]
                if count == 0:
                    # Verificar se existe, mas está inativo
                    self.db_manager.execute(
                        """
                        SELECT COUNT(*) FROM associacoes 
                        WHERE parceiro_id = ? AND loja_id = ?
                        """,
                        (dados.get('parceiro_id'), dados.get('loja_id'))
                    )
                    count_inativo = self.db_manager.fetchone()[0]

                    if count_inativo > 0:
                        return False, "Associação entre parceiro e loja existe, mas está inativa ou pendente!"
                    else:
                        return False, "Não existe associação entre este parceiro e esta loja!"

            # Carregar comprovante existente
            comprovante = Comprovante(self.db_manager)
            if not comprovante.carregar_por_id(comprovante_id):
                return False, f"Comprovante com ID {comprovante_id} não encontrado."

            # Atualizar dados
            if dados.get('parceiro_id'):
                comprovante.parceiro_id = dados.get('parceiro_id')
            if dados.get('loja_id'):
                comprovante.loja_id = dados.get('loja_id')
            if dados.get('data_entrega'):
                comprovante.data_entrega = dados.get('data_entrega')
            if dados.get('arquivo'):
                # Verificar se o arquivo existe
                arquivo = dados.get('arquivo')
                comprovantes_dir = self._obter_diretorio_comprovantes()
                caminho_arquivo = os.path.join(comprovantes_dir, arquivo)

                if not os.path.exists(caminho_arquivo):
                    return False, f"Arquivo '{arquivo}' não encontrado no diretório de comprovantes!"

                comprovante.arquivo = arquivo

            # Sempre atualizar observações (podem ser vazias)
            comprovante.observacoes = dados.get('observacoes', '')

            if comprovante.salvar():
                nome_parceiro = self._obter_nome_parceiro(comprovante.parceiro_id)
                nome_loja = self._obter_nome_loja(comprovante.loja_id)
                self.logger.info(
                    f"Comprovante de entrega (ID: {comprovante_id}) para '{nome_parceiro}' na loja '{nome_loja}' atualizado com sucesso.")
                return True, f"Comprovante de entrega atualizado com sucesso!"
            else:
                return False, "Erro ao atualizar comprovante. Verifique os dados e tente novamente."

        except Exception as e:
            self.logger.error(f"Erro inesperado ao editar comprovante: {str(e)}")
            return False, f"Erro ao editar comprovante: {str(e)}"

    def excluir_comprovante(self, comprovante_id):
        """
        Exclui um comprovante de entrega.

        Args:
            comprovante_id (int): ID do comprovante a ser excluído.

        Returns:
            bool: True se o comprovante foi excluído com sucesso, False caso contrário.
            str: Mensagem de erro, se houver, ou mensagem de sucesso.
        """
        try:
            # Carregar comprovante
            comprovante = Comprovante(self.db_manager)
            if not comprovante.carregar_por_id(comprovante_id):
                return False, f"Comprovante com ID {comprovante_id} não encontrado."

            # Excluir comprovante
            if comprovante.excluir():
                self.logger.info(f"Comprovante de entrega (ID: {comprovante_id}) excluído com sucesso.")
                return True, f"Comprovante de entrega excluído com sucesso!"
            else:
                return False, "Erro ao excluir comprovante. Tente novamente."

        except Exception as e:
            self.logger.error(f"Erro ao excluir comprovante: {str(e)}")
            return False, f"Erro ao excluir comprovante: {str(e)}"

    def listar_comprovantes(self):
        """
        Lista todos os comprovantes cadastrados.

        Returns:
            list: Lista de tuplas contendo os dados dos comprovantes.
        """
        try:
            return Comprovante.listar_todos(self.db_manager)
        except Exception as e:
            self.logger.error(f"Erro ao listar comprovantes: {str(e)}")
            return []

    def pesquisar_comprovantes_por_parceiro(self, termo):
        """
        Pesquisa comprovantes por parceiro.

        Args:
            termo (str): Termo a ser pesquisado no nome do parceiro.

        Returns:
            list: Lista de tuplas contendo os dados dos comprovantes encontrados.
        """
        try:
            return Comprovante.pesquisar_por_parceiro(self.db_manager, termo)
        except Exception as e:
            self.logger.error(f"Erro ao pesquisar comprovantes por parceiro: {str(e)}")
            return []

    def pesquisar_comprovantes_por_loja(self, termo):
        """
        Pesquisa comprovantes por loja.

        Args:
            termo (str): Termo a ser pesquisado no nome da loja.

        Returns:
            list: Lista de tuplas contendo os dados dos comprovantes encontrados.
        """
        try:
            return Comprovante.pesquisar_por_loja(self.db_manager, termo)
        except Exception as e:
            self.logger.error(f"Erro ao pesquisar comprovantes por loja: {str(e)}")
            return []

    def pesquisar_comprovantes_por_periodo(self, data_inicio, data_fim):
        """
        Pesquisa comprovantes por período de data de entrega.

        Args:
            data_inicio (str): Data inicial no formato 'YYYY-MM-DD'.
            data_fim (str): Data final no formato 'YYYY-MM-DD'.

        Returns:
            list: Lista de tuplas contendo os dados dos comprovantes encontrados.
        """
        try:
            return Comprovante.pesquisar_por_periodo(self.db_manager, data_inicio, data_fim)
        except Exception as e:
            self.logger.error(f"Erro ao pesquisar comprovantes por período: {str(e)}")
            return []

    def obter_comprovante(self, comprovante_id):
        """
        Obtém os dados de um comprovante específico.

        Args:
            comprovante_id (int): ID do comprovante.

        Returns:
            dict: Dicionário com os dados do comprovante ou None se não encontrado.
        """
        try:
            comprovante = Comprovante(self.db_manager)
            if comprovante.carregar_por_id(comprovante_id):
                return comprovante.to_dict()
            return None
        except Exception as e:
            self.logger.error(f"Erro ao obter comprovante: {str(e)}")
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

    def _obter_nome_parceiro(self, parceiro_id):
        """
        Obtém o nome de um parceiro pelo ID.

        Args:
            parceiro_id (int): ID do parceiro.

        Returns:
            str: Nome do parceiro ou string vazia se não encontrado.
        """
        try:
            self.db_manager.execute("SELECT nome FROM parceiros WHERE id = ?", (parceiro_id,))
            resultado = self.db_manager.fetchone()
            return resultado[0] if resultado else ""
        except Exception as e:
            self.logger.error(f"Erro ao obter nome do parceiro: {str(e)}")
            return ""

    def _obter_nome_loja(self, loja_id):
        """
        Obtém o nome de uma loja pelo ID.

        Args:
            loja_id (int): ID da loja.

        Returns:
            str: Nome da loja ou string vazia se não encontrada.
        """
        try:
            self.db_manager.execute("SELECT nome FROM lojas WHERE id = ?", (loja_id,))
            resultado = self.db_manager.fetchone()
            return resultado[0] if resultado else ""
        except Exception as e:
            self.logger.error(f"Erro ao obter nome da loja: {str(e)}")
            return ""

    def _obter_diretorio_comprovantes(self):
        """Obtém o diretório de comprovantes a partir da configuração."""
        try:
            # Tentar obter do arquivo de configuração
            import os
            import configparser

            config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.ini')
            config = configparser.ConfigParser()
            config.read(config_path)
            comprovantes_dir = config['COMPROVANTES']['path']

            # Verificar se o diretório existe
            if not os.path.exists(comprovantes_dir):
                os.makedirs(comprovantes_dir, exist_ok=True)

            return comprovantes_dir
        except Exception as e:
            self.logger.error(f"Erro ao obter diretório de comprovantes: {str(e)}")
            # Usar diretório padrão
            default_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'comprovantes')
            os.makedirs(default_dir, exist_ok=True)
            return default_dir