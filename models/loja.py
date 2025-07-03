#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modelo de Loja
-----------------
Classe para representar e gerenciar os dados de lojas.
"""

import datetime
import sqlite3
import logging
from utils.validators import validar_cnpj, validar_email, formatar_cnpj


class Loja:
    """Classe para representar uma loja."""

    def __init__(self, db_manager):
        """
        Inicializa um objeto Loja.

        Args:
            db_manager (DatabaseManager): Instância do gerenciador de banco de dados.
        """
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)

        # Atributos da loja
        self.id = None
        self.nome = None
        self.cnpj = None
        self.telefone = None
        self.email = None
        self.endereco = None
        self.contato = None
        self.data_cadastro = None
        self.cidade = None
        self.estado = None
        self.agrupamento_id = None

    def carregar_por_id(self, loja_id):
        """
        Carrega os dados de uma loja a partir do ID.

        Args:
            loja_id (int): ID da loja a ser carregada.

        Returns:
            bool: True se a loja foi carregada com sucesso, False caso contrário.
        """
        try:
            self.db_manager.execute(
                """
                SELECT id, nome, cnpj, telefone, email, endereco, contato,
                       data_cadastro, cidade, estado, agrupamento_id
                FROM lojas WHERE id = ?
                """,
                (loja_id,),
            )
            loja = self.db_manager.fetchone()

            if not loja:
                self.logger.warning(f"Loja com ID {loja_id} não encontrada")
                return False

            (
                self.id,
                self.nome,
                self.cnpj,
                self.telefone,
                self.email,
                self.endereco,
                self.contato,
                self.data_cadastro,
                self.cidade,
                self.estado,
                self.agrupamento_id,
            ) = loja
            return True

        except Exception as e:
            self.logger.error(f"Erro ao carregar loja por ID: {str(e)}")
            return False

    def salvar(self):
        """
        Salva os dados da loja no banco de dados.
        Se o ID for None, uma nova loja é inserida.
        Caso contrário, a loja existente é atualizada.

        Returns:
            bool: True se a operação foi bem-sucedida, False caso contrário.
        """
        try:
            # Validar dados obrigatórios
            if not self.nome:
                self.logger.error("Tentativa de salvar loja sem nome")
                return False

            # Validar CNPJ se fornecido
            if self.cnpj and not validar_cnpj(self.cnpj):
                self.logger.error(f"CNPJ inválido: {self.cnpj}")
                return False

            # Validar e-mail se fornecido
            if self.email and not validar_email(self.email):
                self.logger.error(f"E-mail inválido: {self.email}")
                return False

            # Definir a data de cadastro para novas lojas
            if not self.id:
                self.data_cadastro = datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                # Inserir nova loja
                self.db_manager.execute(
                    """
                    INSERT INTO lojas (
                        nome, cnpj, telefone, email, endereco, contato,
                        data_cadastro, cidade, estado, agrupamento_id
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        self.nome,
                        self.cnpj,
                        self.telefone,
                        self.email,
                        self.endereco,
                        self.contato,
                        self.data_cadastro,
                        self.cidade,
                        self.estado,
                        self.agrupamento_id,
                    ),
                )

                # Obter o ID da loja inserida
                self.id = self.db_manager.last_insert_rowid()
                self.logger.info(f"Nova loja inserida com ID {self.id}")

            else:
                # Atualizar loja existente
                self.db_manager.execute(
                    """
                    UPDATE lojas
                    SET nome = ?, cnpj = ?, telefone = ?, email = ?, endereco = ?, contato = ?
                    WHERE id = ?
                    """,
                    (self.nome, self.cnpj, self.telefone, self.email, self.endereco, self.contato, self.id)
                )
                self.logger.info(f"Loja com ID {self.id} atualizada")

            # Commit das alterações
            self.db_manager.commit()
            return True

        except sqlite3.IntegrityError as e:
            self.logger.error(f"Erro de integridade ao salvar loja: {str(e)}")
            if "UNIQUE constraint failed: lojas.cnpj" in str(e):
                raise ValueError("CNPJ já cadastrado para outra loja")
            return False

        except Exception as e:
            self.logger.error(f"Erro ao salvar loja: {str(e)}")
            return False

    def excluir(self):
        """
        Exclui a loja do banco de dados.

        Returns:
            bool: True se a exclusão foi bem-sucedida, False caso contrário.
        """
        if not self.id:
            self.logger.error("Tentativa de excluir loja sem ID")
            return False

        try:
            # Verificar se existem associações ou comprovantes relacionados
            self.db_manager.execute(
                "SELECT COUNT(*) FROM associacoes WHERE loja_id = ?", (self.id,)
            )
            count_associacoes = self.db_manager.fetchone()[0]

            self.db_manager.execute(
                "SELECT COUNT(*) FROM comprovantes WHERE loja_id = ?", (self.id,)
            )
            count_comprovantes = self.db_manager.fetchone()[0]

            # Excluir registros relacionados se existirem
            if count_associacoes > 0:
                self.db_manager.execute(
                    "DELETE FROM associacoes WHERE loja_id = ?", (self.id,)
                )
                self.logger.info(
                    f"Excluídas {count_associacoes} associações relacionadas à loja {self.id}"
                )

            if count_comprovantes > 0:
                self.db_manager.execute(
                    "DELETE FROM comprovantes WHERE loja_id = ?", (self.id,)
                )
                self.logger.info(
                    f"Excluídos {count_comprovantes} comprovantes relacionados à loja {self.id}"
                )

            # Excluir a loja
            self.db_manager.execute("DELETE FROM lojas WHERE id = ?", (self.id,))

            # Commit das alterações
            self.db_manager.commit()

            self.logger.info(f"Loja com ID {self.id} excluída")
            self.id = None
            return True

        except Exception as e:
            self.logger.error(f"Erro ao excluir loja: {str(e)}")
            return False

    @classmethod
    def listar_todas(cls, db_manager):
        """
        Lista todas as lojas cadastradas.

        Args:
            db_manager (DatabaseManager): Instância do gerenciador de banco de dados.

        Returns:
            list: Lista de tuplas contendo os dados das lojas.
        """
        try:
            db_manager.execute(
                """
                SELECT id, nome, cnpj, telefone, email, endereco, contato,
                       data_cadastro, cidade, estado, agrupamento_id
                FROM lojas
                WHERE nome LIKE ? OR cnpj LIKE ? OR telefone LIKE ?
                      OR email LIKE ? OR contato LIKE ?
                ORDER BY nome
                """,
                (
                    f"%{termo}%",
                    f"%{termo}%",
                    f"%{termo}%",
                    f"%{termo}%",
                    f"%{termo}%",
                ),
            )
            return db_manager.fetchall()

        except Exception as e:
            logging.getLogger(__name__).error(f"Erro ao listar lojas: {str(e)}")
            return []

    @classmethod
    def pesquisar(cls, db_manager, termo):
        """
        Pesquisa lojas por termo em vários campos.

        Args:
            db_manager (DatabaseManager): Instância do gerenciador de banco de dados.
            termo (str): Termo a ser pesquisado.

        Returns:
            list: Lista de tuplas contendo os dados das lojas encontradas.
        """
        try:
            db_manager.execute(
                """
                SELECT id, nome, cnpj, telefone, email, endereco, contato, data_cadastro 
                FROM lojas 
                WHERE nome LIKE ? OR cnpj LIKE ? OR telefone LIKE ? 
                      OR email LIKE ? OR contato LIKE ?
                ORDER BY nome
                """,
                (f"%{termo}%", f"%{termo}%", f"%{termo}%", f"%{termo}%", f"%{termo}%")
            )
            return db_manager.fetchall()

        except Exception as e:
            logging.getLogger(__name__).error(f"Erro ao pesquisar lojas: {str(e)}")
            return []

    def to_dict(self):
        """
        Converte os dados da loja para um dicionário.

        Returns:
            dict: Dicionário com os dados da loja.
        """
        return {
            "id": self.id,
            "nome": self.nome,
            "cnpj": formatar_cnpj(self.cnpj) if self.cnpj else "",
            "telefone": self.telefone,
            "email": self.email,
            "endereco": self.endereco,
            "contato": self.contato,
            "data_cadastro": self.data_cadastro,
            "cidade": self.cidade,
            "estado": self.estado,
            "agrupamento_id": self.agrupamento_id,
        }