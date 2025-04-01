#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modelo de Associação
------------------
Classe para representar e gerenciar os dados de associações entre parceiros e lojas.
"""

import datetime
import sqlite3
import logging


class Associacao:
    """Classe para representar uma associação entre parceiro e loja."""

    def __init__(self, db_manager):
        """
        Inicializa um objeto Associacao.

        Args:
            db_manager (DatabaseManager): Instância do gerenciador de banco de dados.
        """
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)

        # Atributos da associação
        self.id = None
        self.parceiro_id = None
        self.loja_id = None
        self.status = None
        self.observacao = None
        self.data_associacao = None

    def carregar_por_id(self, associacao_id):
        """
        Carrega os dados de uma associação a partir do ID.

        Args:
            associacao_id (int): ID da associação a ser carregada.

        Returns:
            bool: True se a associação foi carregada com sucesso, False caso contrário.
        """
        try:
            self.db_manager.execute(
                """
                SELECT id, parceiro_id, loja_id, status, observacao, data_associacao 
                FROM associacoes 
                WHERE id = ?
                """,
                (associacao_id,)
            )
            associacao = self.db_manager.fetchone()

            if not associacao:
                self.logger.warning(f"Associação com ID {associacao_id} não encontrada")
                return False

            self.id, self.parceiro_id, self.loja_id, self.status, self.observacao, self.data_associacao = associacao
            return True

        except Exception as e:
            self.logger.error(f"Erro ao carregar associação por ID: {str(e)}")
            return False

    def salvar(self):
        """
        Salva os dados da associação no banco de dados.
        Se o ID for None, uma nova associação é inserida.
        Caso contrário, a associação existente é atualizada.

        Returns:
            bool: True se a operação foi bem-sucedida, False caso contrário.
        """
        try:
            # Validar dados obrigatórios
            if not self.parceiro_id:
                self.logger.error("Tentativa de salvar associação sem parceiro_id")
                return False

            if not self.loja_id:
                self.logger.error("Tentativa de salvar associação sem loja_id")
                return False

            if not self.status:
                self.status = "Ativo"  # Valor padrão

            # Definir a data de associação para novas associações
            if not self.id:
                self.data_associacao = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Inserir nova associação
                self.db_manager.execute(
                    """
                    INSERT INTO associacoes (parceiro_id, loja_id, status, observacao, data_associacao)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (self.parceiro_id, self.loja_id, self.status, self.observacao, self.data_associacao)
                )

                # Obter o ID da associação inserida
                self.id = self.db_manager.last_insert_rowid()
                self.logger.info(f"Nova associação inserida com ID {self.id}")

            else:
                # Atualizar associação existente
                self.db_manager.execute(
                    """
                    UPDATE associacoes
                    SET parceiro_id = ?, loja_id = ?, status = ?, observacao = ?
                    WHERE id = ?
                    """,
                    (self.parceiro_id, self.loja_id, self.status, self.observacao, self.id)
                )
                self.logger.info(f"Associação com ID {self.id} atualizada")

            # Commit das alterações
            self.db_manager.commit()
            return True

        except sqlite3.IntegrityError as e:
            self.logger.error(f"Erro de integridade ao salvar associação: {str(e)}")
            if "UNIQUE constraint failed" in str(e):
                raise ValueError("Já existe uma associação entre este parceiro e esta loja")
            return False

        except Exception as e:
            self.logger.error(f"Erro ao salvar associação: {str(e)}")
            return False

    def excluir(self):
        """
        Exclui a associação do banco de dados.

        Returns:
            bool: True se a exclusão foi bem-sucedida, False caso contrário.
        """
        if not self.id:
            self.logger.error("Tentativa de excluir associação sem ID")
            return False

        try:
            # Verificar se existem comprovantes usando esta associação
            self.db_manager.execute(
                """
                SELECT COUNT(*) FROM comprovantes 
                WHERE parceiro_id = ? AND loja_id = ?
                """,
                (self.parceiro_id, self.loja_id)
            )
            count = self.db_manager.fetchone()[0]

            if count > 0:
                self.logger.warning(
                    f"Tentativa de excluir associação com {count} comprovantes vinculados"
                )
                return False

            # Excluir a associação
            self.db_manager.execute(
                "DELETE FROM associacoes WHERE id = ?",
                (self.id,)
            )

            # Commit das alterações
            self.db_manager.commit()

            self.logger.info(f"Associação com ID {self.id} excluída")
            self.id = None
            return True

        except Exception as e:
            self.logger.error(f"Erro ao excluir associação: {str(e)}")
            return False

    @classmethod
    def listar_todas(cls, db_manager):
        """
        Lista todas as associações cadastradas.

        Args:
            db_manager (DatabaseManager): Instância do gerenciador de banco de dados.

        Returns:
            list: Lista de tuplas contendo os dados das associações.
        """
        try:
            db_manager.execute(
                """
                SELECT a.id, p.nome, l.nome, a.status, a.observacao, a.data_associacao
                FROM associacoes a
                JOIN parceiros p ON a.parceiro_id = p.id
                JOIN lojas l ON a.loja_id = l.id
                ORDER BY p.nome, l.nome
                """
            )
            return db_manager.fetchall()

        except Exception as e:
            logging.getLogger(__name__).error(f"Erro ao listar associações: {str(e)}")
            return []

    @classmethod
    def pesquisar(cls, db_manager, termo):
        """
        Pesquisa associações por termo.

        Args:
            db_manager (DatabaseManager): Instância do gerenciador de banco de dados.
            termo (str): Termo a ser pesquisado.

        Returns:
            list: Lista de tuplas contendo os dados das associações encontradas.
        """
        try:
            db_manager.execute(
                """
                SELECT a.id, p.nome, l.nome, a.status, a.observacao, a.data_associacao
                FROM associacoes a
                JOIN parceiros p ON a.parceiro_id = p.id
                JOIN lojas l ON a.loja_id = l.id
                WHERE p.nome LIKE ? OR l.nome LIKE ? OR a.status LIKE ? OR a.observacao LIKE ?
                ORDER BY p.nome, l.nome
                """,
                (f"%{termo}%", f"%{termo}%", f"%{termo}%", f"%{termo}%")
            )
            return db_manager.fetchall()

        except Exception as e:
            logging.getLogger(__name__).error(f"Erro ao pesquisar associações: {str(e)}")
            return []

    @classmethod
    def filtrar(cls, db_manager, parceiro_id=None, loja_id=None, status=None):
        """
        Filtra associações por parceiro, loja e/ou status.

        Args:
            db_manager (DatabaseManager): Instância do gerenciador de banco de dados.
            parceiro_id (int, optional): ID do parceiro para filtrar.
            loja_id (int, optional): ID da loja para filtrar.
            status (str, optional): Status para filtrar.

        Returns:
            list: Lista de tuplas contendo os dados das associações filtradas.
        """
        try:
            # Construir consulta SQL com filtros dinâmicos
            sql = """
                SELECT a.id, p.nome, l.nome, a.status, a.observacao, a.data_associacao
                FROM associacoes a
                JOIN parceiros p ON a.parceiro_id = p.id
                JOIN lojas l ON a.loja_id = l.id
                WHERE 1=1
            """
            params = []

            if parceiro_id:
                sql += " AND a.parceiro_id = ?"
                params.append(parceiro_id)

            if loja_id:
                sql += " AND a.loja_id = ?"
                params.append(loja_id)

            if status:
                sql += " AND a.status = ?"
                params.append(status)

            sql += " ORDER BY p.nome, l.nome"

            db_manager.execute(sql, tuple(params))
            return db_manager.fetchall()

        except Exception as e:
            logging.getLogger(__name__).error(f"Erro ao filtrar associações: {str(e)}")
            return []

    @classmethod
    def verificar_associacao(cls, db_manager, parceiro_id, loja_id):
        """
        Verifica se existe uma associação entre parceiro e loja.

        Args:
            db_manager (DatabaseManager): Instância do gerenciador de banco de dados.
            parceiro_id (int): ID do parceiro.
            loja_id (int): ID da loja.

        Returns:
            tuple: (bool, dict) Indica se existe associação e seus detalhes (None se não existir).
        """
        try:
            db_manager.execute(
                """
                SELECT id, status, observacao, data_associacao 
                FROM associacoes 
                WHERE parceiro_id = ? AND loja_id = ?
                """,
                (parceiro_id, loja_id)
            )

            result = db_manager.fetchone()

            if result:
                # Retorna True e detalhes da associação
                return True, {
                    'id': result[0],
                    'status': result[1],
                    'observacao': result[2],
                    'data_associacao': result[3]
                }

            # Não existe associação
            return False, None

        except Exception as e:
            logging.getLogger(__name__).error(f"Erro ao verificar associação: {str(e)}")
            return False, None

    def to_dict(self):
        """
        Converte os dados da associação para um dicionário.

        Returns:
            dict: Dicionário com os dados da associação.
        """
        return {
            'id': self.id,
            'parceiro_id': self.parceiro_id,
            'loja_id': self.loja_id,
            'status': self.status,
            'observacao': self.observacao,
            'data_associacao': self.data_associacao
        }