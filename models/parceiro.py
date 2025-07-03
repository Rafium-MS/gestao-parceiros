#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modelo de Parceiro
-----------------
Classe para representar e gerenciar os dados de parceiros.
"""

import datetime
import sqlite3
import logging
from utils.validators import validar_cpf, validar_email, formatar_cpf


class Parceiro:
    """Classe para representar um parceiro."""

    def __init__(self, db_manager):
        """
        Inicializa um objeto Parceiro.

        Args:
            db_manager (DatabaseManager): Instância do gerenciador de banco de dados.
        """
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)

        # Atributos do parceiro
        self.id = None
        self.nome = None
        self.cpf = None
        self.telefone = None
        self.email = None
        self.endereco = None
        self.data_cadastro = None
        self.cidade = None
        self.estado = None
        self.banco = None
        self.agencia = None
        self.conta = None
        self.tipo = None
        self.produto = None
        self.valor_unidade = None

    def carregar_por_id(self, parceiro_id):
        """
        Carrega os dados de um parceiro a partir do ID.

        Args:
            parceiro_id (int): ID do parceiro a ser carregado.

        Returns:
            bool: True se o parceiro foi carregado com sucesso, False caso contrário.
        """
        try:
            self.db_manager.execute(
                """
                SELECT id, nome, cpf, telefone, email, endereco, data_cadastro,
                       cidade, estado, banco, agencia, conta, tipo, produto,
                       valor_unidade
                FROM parceiros WHERE id = ?
                """,
                (parceiro_id,),
            )
            parceiro = self.db_manager.fetchone()

            if not parceiro:
                self.logger.warning(f"Parceiro com ID {parceiro_id} não encontrado")
                return False

            (
                self.id,
                self.nome,
                self.cpf,
                self.telefone,
                self.email,
                self.endereco,
                self.data_cadastro,
                self.cidade,
                self.estado,
                self.banco,
                self.agencia,
                self.conta,
                self.tipo,
                self.produto,
                self.valor_unidade,
            ) = parceiro
            return True

        except Exception as e:
            self.logger.error(f"Erro ao carregar parceiro por ID: {str(e)}")
            return False

    def salvar(self):
        """
        Salva os dados do parceiro no banco de dados.
        Se o ID for None, um novo parceiro é inserido.
        Caso contrário, o parceiro existente é atualizado.

        Returns:
            bool: True se a operação foi bem-sucedida, False caso contrário.
        """
        try:
            # Validar dados obrigatórios
            if not self.nome:
                self.logger.error("Tentativa de salvar parceiro sem nome")
                return False

            # Validar CPF se fornecido
            if self.cpf and not validar_cpf(self.cpf):
                self.logger.error(f"CPF inválido: {self.cpf}")
                return False

            # Validar e-mail se fornecido
            if self.email and not validar_email(self.email):
                self.logger.error(f"E-mail inválido: {self.email}")
                return False

            # Definir a data de cadastro para novos parceiros
            if not self.id:
                self.data_cadastro = datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                # Inserir novo parceiro
                self.db_manager.execute(
                    """
                    INSERT INTO parceiros (
                        nome, cpf, telefone, email, endereco, data_cadastro,
                        cidade, estado, banco, agencia, conta, tipo, produto,
                        valor_unidade
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        self.nome,
                        self.cpf,
                        self.telefone,
                        self.email,
                        self.endereco,
                        self.data_cadastro,
                        self.cidade,
                        self.estado,
                        self.banco,
                        self.agencia,
                        self.conta,
                        self.tipo,
                        self.produto,
                        self.valor_unidade,
                    ),
                )

                # Obter o ID do parceiro inserido
                self.id = self.db_manager.last_insert_rowid()
                self.logger.info(f"Novo parceiro inserido com ID {self.id}")

            else:
                # Atualizar parceiro existente
                self.db_manager.execute(
                    """
                    UPDATE parceiros
                    SET nome = ?, cpf = ?, telefone = ?, email = ?, endereco = ?,
                        cidade = ?, estado = ?, banco = ?, agencia = ?, conta = ?,
                        tipo = ?, produto = ?, valor_unidade = ?                    WHERE id = ?
                    """,
                    (
                        self.nome,
                        self.cpf,
                        self.telefone,
                        self.email,
                        self.endereco,
                        self.cidade,
                        self.estado,
                        self.banco,
                        self.agencia,
                        self.conta,
                        self.tipo,
                        self.produto,
                        self.valor_unidade,
                        self.id,
                    ),
                )
                self.logger.info(f"Parceiro com ID {self.id} atualizado")

            # Commit das alterações
            self.db_manager.commit()
            return True

        except sqlite3.IntegrityError as e:
            self.logger.error(f"Erro de integridade ao salvar parceiro: {str(e)}")
            if "UNIQUE constraint failed: parceiros.cpf" in str(e):
                raise ValueError("CPF já cadastrado para outro parceiro")
            return False

        except Exception as e:
            self.logger.error(f"Erro ao salvar parceiro: {str(e)}")
            return False

    def excluir(self):
        """
        Exclui o parceiro do banco de dados.

        Returns:
            bool: True se a exclusão foi bem-sucedida, False caso contrário.
        """
        if not self.id:
            self.logger.error("Tentativa de excluir parceiro sem ID")
            return False

        try:
            # Verificar se existem associações ou comprovantes relacionados
            self.db_manager.execute(
                "SELECT COUNT(*) FROM associacoes WHERE parceiro_id = ?", (self.id,)
            )
            count_associacoes = self.db_manager.fetchone()[0]

            self.db_manager.execute(
                "SELECT COUNT(*) FROM comprovantes WHERE parceiro_id = ?", (self.id,)

            )
            count_comprovantes = self.db_manager.fetchone()[0]

            # Excluir registros relacionados se existirem
            if count_associacoes > 0:
                self.db_manager.execute(
                    "DELETE FROM associacoes WHERE parceiro_id = ?", (self.id,)
                )
                self.logger.info(
                    f"Excluídas {count_associacoes} associações relacionadas ao parceiro {self.id}"
                )

            if count_comprovantes > 0:
                self.db_manager.execute(
                    "DELETE FROM comprovantes WHERE parceiro_id = ?", (self.id,)
                )
                self.logger.info(
                    f"Excluídos {count_comprovantes} comprovantes relacionados ao parceiro {self.id}"
                )

            # Excluir o parceiro
            self.db_manager.execute("DELETE FROM parceiros WHERE id = ?", (self.id,))

            # Commit das alterações
            self.db_manager.commit()

            self.logger.info(f"Parceiro com ID {self.id} excluído")
            self.id = None
            return True

        except Exception as e:
            self.logger.error(f"Erro ao excluir parceiro: {str(e)}")
            return False

    @classmethod
    def listar_todos(cls, db_manager):
        """
        Lista todos os parceiros cadastrados.

        Args:
            db_manager (DatabaseManager): Instância do gerenciador de banco de dados.

        Returns:
            list: Lista de tuplas contendo os dados dos parceiros.
        """
        try:
            db_manager.execute(
                """
                SELECT id, nome, cpf, telefone, email, endereco, data_cadastro,
                       cidade, estado, banco, agencia, conta, tipo, produto,
                       valor_unidade
                FROM parceiros
                ORDER BY nome
                """            )
            return db_manager.fetchall()

        except Exception as e:
            logging.getLogger(__name__).error(f"Erro ao listar parceiros: {str(e)}")
            return []

    @classmethod
    def pesquisar(cls, db_manager, termo):
        """
        Pesquisa parceiros por termo em vários campos.

        Args:
            db_manager (DatabaseManager): Instância do gerenciador de banco de dados.
            termo (str): Termo a ser pesquisado.

        Returns:
            list: Lista de tuplas contendo os dados dos parceiros encontrados.
        """
        try:
            db_manager.execute(
                """
                SELECT id, nome, cpf, telefone, email, endereco, data_cadastro,
                       cidade, estado, banco, agencia, conta, tipo, produto,
                       valor_unidade
                FROM parceiros
                WHERE nome LIKE ? OR cpf LIKE ? OR telefone LIKE ? OR email LIKE ?
                ORDER BY nome
                """,
                (f"%{termo}%", f"%{termo}%", f"%{termo}%", f"%{termo}%"),
            )
            return db_manager.fetchall()

        except Exception as e:
            logging.getLogger(__name__).error(f"Erro ao pesquisar parceiros: {str(e)}")
            return []

    def to_dict(self):
        """
        Converte os dados do parceiro para um dicionário.

        Returns:
            dict: Dicionário com os dados do parceiro.
        """
        return {
            "id": self.id,
            "nome": self.nome,
            "cpf": formatar_cpf(self.cpf) if self.cpf else "",
            "telefone": self.telefone,
            "email": self.email,
            "endereco": self.endereco,
            "data_cadastro": self.data_cadastro,
            "cidade": self.cidade,
            "estado": self.estado,
            "banco": self.banco,
            "agencia": self.agencia,
            "conta": self.conta,
            "tipo": self.tipo,
            "produto": self.produto,
            "valor_unidade": self.valor_unidade,
        }