#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modelo de Comprovante
-------------------
Classe para representar e gerenciar os dados de comprovantes de entrega.
"""

import os
import datetime
import logging
import shutil
import sqlite3
import uuid


class Comprovante:
    """Classe para representar um comprovante de entrega."""

    def __init__(self, db_manager):
        """
        Inicializa um objeto Comprovante.

        Args:
            db_manager (DatabaseManager): Instância do gerenciador de banco de dados.
        """
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)

        # Atributos do comprovante
        self.id = None
        self.parceiro_id = None
        self.loja_id = None
        self.data_entrega = None
        self.arquivo_comprovante = None
        self.observacoes = None
        self.data_cadastro = None

    def carregar_por_id(self, comprovante_id):
        """
        Carrega os dados de um comprovante a partir do ID.

        Args:
            comprovante_id (int): ID do comprovante a ser carregado.

        Returns:
            bool: True se o comprovante foi carregado com sucesso, False caso contrário.
        """
        try:
            self.db_manager.execute(
                """
                SELECT id, parceiro_id, loja_id, data_entrega, arquivo_comprovante, 
                       observacoes, data_cadastro 
                FROM comprovantes WHERE id = ?
                """,
                (comprovante_id,)
            )
            comprovante = self.db_manager.fetchone()

            if not comprovante:
                self.logger.warning(f"Comprovante com ID {comprovante_id} não encontrado")
                return False

            (
                self.id,
                self.parceiro_id,
                self.loja_id,
                self.data_entrega,
                self.arquivo_comprovante,
                self.observacoes,
                self.data_cadastro
            ) = comprovante

            return True

        except Exception as e:
            self.logger.error(f"Erro ao carregar comprovante por ID: {str(e)}")
            return False

    def salvar(self, arquivo_origem=None):
        """
        Salva os dados do comprovante no banco de dados.
        Se o ID for None, um novo comprovante é inserido.
        Caso contrário, o comprovante existente é atualizado.

        Args:
            arquivo_origem (str, optional): Caminho do arquivo de origem do comprovante.
                Se fornecido, o arquivo será copiado para o diretório de comprovantes.

        Returns:
            bool: True se a operação foi bem-sucedida, False caso contrário.
        """
        try:
            # Validar dados obrigatórios
            if not self.parceiro_id or not self.loja_id or not self.data_entrega:
                self.logger.error("Dados obrigatórios não fornecidos para o comprovante")
                return False

            # Se um novo arquivo foi fornecido, copiar para o diretório de comprovantes
            if arquivo_origem and os.path.exists(arquivo_origem):
                # Gerar nome único para o arquivo
                extensao = os.path.splitext(arquivo_origem)[1].lower()
                nome_arquivo = f"{uuid.uuid4()}{extensao}"

                # Definir diretório de destino
                comprovantes_dir = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "comprovantes"
                )

                # Verificar se o diretório existe, criar se necessário
                if not os.path.exists(comprovantes_dir):
                    os.makedirs(comprovantes_dir)

                # Caminho completo de destino
                caminho_destino = os.path.join(comprovantes_dir, nome_arquivo)

                # Copiar arquivo
                shutil.copy2(arquivo_origem, caminho_destino)
                self.logger.info(f"Arquivo copiado: {arquivo_origem} -> {caminho_destino}")

                # Atualizar nome do arquivo no objeto
                self.arquivo_comprovante = nome_arquivo

            # Definir a data de cadastro para novos comprovantes
            if not self.id:
                self.data_cadastro = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Inserir novo comprovante
                self.db_manager.execute(
                    """
                    INSERT INTO comprovantes (
                        parceiro_id, loja_id, data_entrega, arquivo_comprovante, 
                        observacoes, data_cadastro
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        self.parceiro_id, self.loja_id, self.data_entrega,
                        self.arquivo_comprovante, self.observacoes, self.data_cadastro
                    )
                )

                # Obter o ID do comprovante inserido
                self.id = self.db_manager.last_insert_rowid()
                self.logger.info(f"Novo comprovante inserido com ID {self.id}")

            else:
                # Se não foi fornecido um novo arquivo, manter o atual
                if not self.arquivo_comprovante:
                    # Recuperar o nome do arquivo atual
                    self.db_manager.execute(
                        "SELECT arquivo_comprovante FROM comprovantes WHERE id = ?",
                        (self.id,)
                    )
                    resultado = self.db_manager.fetchone()
                    if resultado:
                        self.arquivo_comprovante = resultado[0]

                # Atualizar comprovante existente
                self.db_manager.execute(
                    """
                    UPDATE comprovantes
                    SET parceiro_id = ?, loja_id = ?, data_entrega = ?, 
                        arquivo_comprovante = ?, observacoes = ?
                    WHERE id = ?
                    """,
                    (
                        self.parceiro_id, self.loja_id, self.data_entrega,
                        self.arquivo_comprovante, self.observacoes, self.id
                    )
                )
                self.logger.info(f"Comprovante com ID {self.id} atualizado")

            # Commit das alterações
            self.db_manager.commit()
            return True

        except sqlite3.IntegrityError as e:
            self.logger.error(f"Erro de integridade ao salvar comprovante: {str(e)}")
            self.db_manager.rollback()
            return False

        except Exception as e:
            self.logger.error(f"Erro ao salvar comprovante: {str(e)}")
            self.db_manager.rollback()
            return False

    def excluir(self):
        """
        Exclui o comprovante do banco de dados e remove o arquivo associado.

        Returns:
            bool: True se a exclusão foi bem-sucedida, False caso contrário.
        """
        if not self.id:
            self.logger.error("Tentativa de excluir comprovante sem ID")
            return False

        try:
            # Recuperar o nome do arquivo antes de excluir o registro
            arquivo = self.arquivo_comprovante

            # Excluir o registro do banco de dados
            self.db_manager.execute(
                "DELETE FROM comprovantes WHERE id = ?",
                (self.id,)
            )

            # Commit das alterações
            self.db_manager.commit()

            # Tentar excluir o arquivo físico se existir
            if arquivo:
                comprovantes_dir = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "comprovantes"
                )
                caminho_arquivo = os.path.join(comprovantes_dir, arquivo)

                if os.path.exists(caminho_arquivo):
                    os.remove(caminho_arquivo)
                    self.logger.info(f"Arquivo de comprovante excluído: {caminho_arquivo}")
                else:
                    self.logger.warning(f"Arquivo de comprovante não encontrado: {caminho_arquivo}")

            self.logger.info(f"Comprovante com ID {self.id} excluído")
            self.id = None
            return True

        except Exception as e:
            self.logger.error(f"Erro ao excluir comprovante: {str(e)}")
            self.db_manager.rollback()
            return False

    @classmethod
    def listar_todos(cls, db_manager):
        """
        Lista todos os comprovantes cadastrados.

        Args:
            db_manager (DatabaseManager): Instância do gerenciador de banco de dados.

        Returns:
            list: Lista de tuplas contendo os dados dos comprovantes.
        """
        try:
            db_manager.execute(
                """
                SELECT c.id, p.nome as parceiro, l.nome as loja, 
                       c.data_entrega, c.arquivo_comprovante, c.observacoes
                FROM comprovantes c
                JOIN parceiros p ON c.parceiro_id = p.id
                JOIN lojas l ON c.loja_id = l.id
                ORDER BY c.data_entrega DESC
                """
            )
            return db_manager.fetchall()

        except Exception as e:
            logging.getLogger(__name__).error(f"Erro ao listar comprovantes: {str(e)}")
            return []

    @classmethod
    def listar_por_parceiro(cls, db_manager, parceiro_id):
        """
        Lista os comprovantes de um parceiro específico.

        Args:
            db_manager (DatabaseManager): Instância do gerenciador de banco de dados.
            parceiro_id (int): ID do parceiro.

        Returns:
            list: Lista de tuplas contendo os dados dos comprovantes.
        """
        try:
            db_manager.execute(
                """
                SELECT c.id, p.nome as parceiro, l.nome as loja, 
                       c.data_entrega, c.arquivo_comprovante, c.observacoes
                FROM comprovantes c
                JOIN parceiros p ON c.parceiro_id = p.id
                JOIN lojas l ON c.loja_id = l.id
                WHERE c.parceiro_id = ?
                ORDER BY c.data_entrega DESC
                """,
                (parceiro_id,)
            )
            return db_manager.fetchall()

        except Exception as e:
            logging.getLogger(__name__).error(f"Erro ao listar comprovantes por parceiro: {str(e)}")
            return []

    @classmethod
    def listar_por_loja(cls, db_manager, loja_id):
        """
        Lista os comprovantes de uma loja específica.

        Args:
            db_manager (DatabaseManager): Instância do gerenciador de banco de dados.
            loja_id (int): ID da loja.

        Returns:
            list: Lista de tuplas contendo os dados dos comprovantes.
        """
        try:
            db_manager.execute(
                """
                SELECT c.id, p.nome as parceiro, l.nome as loja, 
                       c.data_entrega, c.arquivo_comprovante, c.observacoes
                FROM comprovantes c
                JOIN parceiros p ON c.parceiro_id = p.id
                JOIN lojas l ON c.loja_id = l.id
                WHERE c.loja_id = ?
                ORDER BY c.data_entrega DESC
                """,
                (loja_id,)
            )
            return db_manager.fetchall()

        except Exception as e:
            logging.getLogger(__name__).error(f"Erro ao listar comprovantes por loja: {str(e)}")
            return []

    @classmethod
    def listar_por_periodo(cls, db_manager, data_inicial, data_final):
        """
        Lista os comprovantes de um período específico.

        Args:
            db_manager (DatabaseManager): Instância do gerenciador de banco de dados.
            data_inicial (str): Data inicial no formato YYYY-MM-DD.
            data_final (str): Data final no formato YYYY-MM-DD.

        Returns:
            list: Lista de tuplas contendo os dados dos comprovantes.
        """
        try:
            db_manager.execute(
                """
                SELECT c.id, p.nome as parceiro, l.nome as loja, 
                       c.data_entrega, c.arquivo_comprovante, c.observacoes
                FROM comprovantes c
                JOIN parceiros p ON c.parceiro_id = p.id
                JOIN lojas l ON c.loja_id = l.id
                WHERE c.data_entrega BETWEEN ? AND ?
                ORDER BY c.data_entrega DESC
                """,
                (data_inicial, data_final)
            )
            return db_manager.fetchall()

        except Exception as e:
            logging.getLogger(__name__).error(f"Erro ao listar comprovantes por período: {str(e)}")
            return []

    @classmethod
    def pesquisar(cls, db_manager, termo):
        """
        Pesquisa comprovantes por termo em vários campos.

        Args:
            db_manager (DatabaseManager): Instância do gerenciador de banco de dados.
            termo (str): Termo a ser pesquisado.

        Returns:
            list: Lista de tuplas contendo os dados dos comprovantes encontrados.
        """
        try:
            db_manager.execute(
                """
                SELECT c.id, p.nome as parceiro, l.nome as loja, 
                       c.data_entrega, c.arquivo_comprovante, c.observacoes
                FROM comprovantes c
                JOIN parceiros p ON c.parceiro_id = p.id
                JOIN lojas l ON c.loja_id = l.id
                WHERE p.nome LIKE ? OR l.nome LIKE ? OR c.observacoes LIKE ?
                ORDER BY c.data_entrega DESC
                """,
                (f"%{termo}%", f"%{termo}%", f"%{termo}%")
            )
            return db_manager.fetchall()

        except Exception as e:
            logging.getLogger(__name__).error(f"Erro ao pesquisar comprovantes: {str(e)}")
            return []

    def to_dict(self):
        """
        Converte os dados do comprovante para um dicionário.

        Returns:
            dict: Dicionário com os dados do comprovante.
        """
        return {
            'id': self.id,
            'parceiro_id': self.parceiro_id,
            'loja_id': self.loja_id,
            'data_entrega': self.data_entrega,
            'arquivo_comprovante': self.arquivo_comprovante,
            'observacoes': self.observacoes,
            'data_cadastro': self.data_cadastro
        }