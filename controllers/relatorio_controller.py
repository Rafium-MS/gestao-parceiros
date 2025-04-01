#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Controlador de Relatórios
-----------------------
Gerencia as operações relacionadas aos relatórios, conectando a interface com o modelo de dados.
"""

import logging
import os
import webbrowser
import datetime
from tkinter import messagebox


class RelatorioController:
    """Controlador para gerenciamento de relatórios."""

    def __init__(self, db_manager):
        """
        Inicializa o controlador de relatórios.

        Args:
            db_manager (DatabaseManager): Instância do gerenciador de banco de dados.
        """
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)

    def gerar_relatorio_parceiro(self, parceiro_nome=None, data_inicial=None, data_final=None, loja_nome=None):
        """
        Gera relatório de entregas por parceiro.

        Args:
            parceiro_nome (str, optional): Nome do parceiro filtrado. None para todos.
            data_inicial (str, optional): Data inicial no formato YYYY-MM-DD.
            data_final (str, optional): Data final no formato YYYY-MM-DD.
            loja_nome (str, optional): Nome da loja filtrada. None para todas.

        Returns:
            list: Lista de tuplas com os dados do relatório.
        """
        try:
            # Construir a consulta SQL base
            query = """
                SELECT c.id, p.nome as parceiro, l.nome as loja, 
                       c.data_entrega, c.arquivo_comprovante, c.observacoes
                FROM comprovantes c
                JOIN parceiros p ON c.parceiro_id = p.id
                JOIN lojas l ON c.loja_id = l.id
                WHERE 1=1
            """
            params = []

            # Adicionar filtros
            if parceiro_nome:
                query += " AND p.nome = ?"
                params.append(parceiro_nome)

            if loja_nome:
                query += " AND l.nome = ?"
                params.append(loja_nome)

            if data_inicial:
                query += " AND c.data_entrega >= ?"
                params.append(data_inicial)

            if data_final:
                query += " AND c.data_entrega <= ?"
                params.append(data_final)

            # Ordenar por parceiro e data
            query += " ORDER BY p.nome, c.data_entrega DESC"

            # Executar consulta
            self.db_manager.execute(query, tuple(params))
            resultados = self.db_manager.fetchall()

            self.logger.info(f"Relatório por parceiro gerado: {len(resultados)} registros")
            return resultados

        except Exception as e:
            self.logger.error(f"Erro ao gerar relatório por parceiro: {str(e)}")
            raise

    def gerar_relatorio_loja(self, loja_nome=None, data_inicial=None, data_final=None, parceiro_nome=None):
        """
        Gera relatório de entregas por loja.

        Args:
            loja_nome (str, optional): Nome da loja filtrada. None para todas.
            data_inicial (str, optional): Data inicial no formato YYYY-MM-DD.
            data_final (str, optional): Data final no formato YYYY-MM-DD.
            parceiro_nome (str, optional): Nome do parceiro filtrado. None para todos.

        Returns:
            list: Lista de tuplas com os dados do relatório.
        """
        try:
            # Construir a consulta SQL base
            query = """
                SELECT c.id, p.nome as parceiro, l.nome as loja, 
                       c.data_entrega, c.arquivo_comprovante, c.observacoes
                FROM comprovantes c
                JOIN parceiros p ON c.parceiro_id = p.id
                JOIN lojas l ON c.loja_id = l.id
                WHERE 1=1
            """
            params = []

            # Adicionar filtros
            if loja_nome:
                query += " AND l.nome = ?"
                params.append(loja_nome)

            if parceiro_nome:
                query += " AND p.nome = ?"
                params.append(parceiro_nome)

            if data_inicial:
                query += " AND c.data_entrega >= ?"
                params.append(data_inicial)

            if data_final:
                query += " AND c.data_entrega <= ?"
                params.append(data_final)

            # Ordenar por loja e data
            query += " ORDER BY l.nome, c.data_entrega DESC"

            # Executar consulta
            self.db_manager.execute(query, tuple(params))
            resultados = self.db_manager.fetchall()

            self.logger.info(f"Relatório por loja gerado: {len(resultados)} registros")
            return resultados

        except Exception as e:
            self.logger.error(f"Erro ao gerar relatório por loja: {str(e)}")
            raise

    def gerar_relatorio_periodo(self, data_inicial=None, data_final=None, parceiro_nome=None, loja_nome=None):
        """
        Gera relatório de entregas por período.

        Args:
            data_inicial (str, optional): Data inicial no formato YYYY-MM-DD.
            data_final (str, optional): Data final no formato YYYY-MM-DD.
            parceiro_nome (str, optional): Nome do parceiro filtrado. None para todos.
            loja_nome (str, optional): Nome da loja filtrada. None para todas.

        Returns:
            list: Lista de tuplas com os dados do relatório.
        """
        try:
            # Construir a consulta SQL base
            query = """
                SELECT c.id, p.nome as parceiro, l.nome as loja, 
                       c.data_entrega, c.arquivo_comprovante, c.observacoes
                FROM comprovantes c
                JOIN parceiros p ON c.parceiro_id = p.id
                JOIN lojas l ON c.loja_id = l.id
                WHERE 1=1
            """
            params = []

            # Adicionar filtros
            if data_inicial:
                query += " AND c.data_entrega >= ?"
                params.append(data_inicial)

            if data_final:
                query += " AND c.data_entrega <= ?"
                params.append(data_final)

            if parceiro_nome:
                query += " AND p.nome = ?"
                params.append(parceiro_nome)

            if loja_nome:
                query += " AND l.nome = ?"
                params.append(loja_nome)

            # Ordenar por data
            query += " ORDER BY c.data_entrega DESC"

            # Executar consulta
            self.db_manager.execute(query, tuple(params))
            resultados = self.db_manager.fetchall()

            self.logger.info(f"Relatório por período gerado: {len(resultados)} registros")
            return resultados

        except Exception as e:
            self.logger.error(f"Erro ao gerar relatório por período: {str(e)}")
            raise

    def visualizar_comprovante(self, comprovante_id):
        """
        Abre o arquivo de comprovante para visualização.

        Args:
            comprovante_id (int): ID do comprovante a ser visualizado.

        Returns:
            bool: True se a visualização foi bem-sucedida, False caso contrário.
        """
        try:
            # Obter informações do comprovante
            self.db_manager.execute(
                "SELECT arquivo_comprovante FROM comprovantes WHERE id = ?",
                (comprovante_id,)
            )
            resultado = self.db_manager.fetchone()

            if not resultado:
                messagebox.showwarning("Aviso", "Comprovante não encontrado.")
                return False

            arquivo_comprovante = resultado[0]

            # Verificar se o arquivo existe
            comprovantes_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                            "comprovantes")
            caminho_completo = os.path.join(comprovantes_dir, arquivo_comprovante)

            if not os.path.exists(caminho_completo):
                messagebox.showwarning(
                    "Arquivo não encontrado",
                    f"O arquivo {arquivo_comprovante} não foi encontrado no diretório de comprovantes."
                )
                return False

            # Abrir o arquivo com o visualizador padrão do sistema
            try:
                webbrowser.open(caminho_completo)
                self.logger.info(f"Comprovante visualizado: {arquivo_comprovante}")
                return True
            except Exception as e:
                messagebox.showerror(
                    "Erro",
                    f"Erro ao abrir o arquivo: {str(e)}\n\nCaminho: {caminho_completo}"
                )
                self.logger.error(f"Erro ao abrir comprovante: {str(e)}")
                return False

        except Exception as e:
            self.logger.error(f"Erro ao visualizar comprovante: {str(e)}")
            messagebox.showerror("Erro", f"Erro ao visualizar comprovante: {str(e)}")
            return False

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

    def gerar_estatisticas(self, data_inicial=None, data_final=None):
        """
        Gera estatísticas gerais para o dashboard.

        Args:
            data_inicial (str, optional): Data inicial no formato YYYY-MM-DD.
            data_final (str, optional): Data final no formato YYYY-MM-DD.

        Returns:
            dict: Dicionário com estatísticas do sistema.
        """
        try:
            # Definir período padrão para o mês atual se não especificado
            if not data_inicial or not data_final:
                hoje = datetime.datetime.now()
                primeiro_dia = datetime.datetime(hoje.year, hoje.month, 1)
                data_inicial = primeiro_dia.strftime("%Y-%m-%d")
                data_final = hoje.strftime("%Y-%m-%d")

            estatisticas = {}

            # Total de parceiros
            self.db_manager.execute("SELECT COUNT(*) FROM parceiros")
            estatisticas['total_parceiros'] = self.db_manager.fetchone()[0]

            # Total de lojas
            self.db_manager.execute("SELECT COUNT(*) FROM lojas")
            estatisticas['total_lojas'] = self.db_manager.fetchone()[0]

            # Total de comprovantes
            self.db_manager.execute("SELECT COUNT(*) FROM comprovantes")
            estatisticas['total_comprovantes'] = self.db_manager.fetchone()[0]

            # Comprovantes no período
            self.db_manager.execute(
                "SELECT COUNT(*) FROM comprovantes WHERE data_entrega BETWEEN ? AND ?",
                (data_inicial, data_final)
            )
            estatisticas['comprovantes_periodo'] = self.db_manager.fetchone()[0]

            # Entregas por parceiro no período
            self.db_manager.execute(
                """
                SELECT p.nome, COUNT(c.id) as total
                FROM comprovantes c
                JOIN parceiros p ON c.parceiro_id = p.id
                WHERE c.data_entrega BETWEEN ? AND ?
                GROUP BY p.nome
                ORDER BY total DESC
                LIMIT 5
                """,
                (data_inicial, data_final)
            )
            estatisticas['top_parceiros'] = self.db_manager.fetchall()

            # Entregas por loja no período
            self.db_manager.execute(
                """
                SELECT l.nome, COUNT(c.id) as total
                FROM comprovantes c
                JOIN lojas l ON c.loja_id = l.id
                WHERE c.data_entrega BETWEEN ? AND ?
                GROUP BY l.nome
                ORDER BY total DESC
                LIMIT 5
                """,
                (data_inicial, data_final)
            )
            estatisticas['top_lojas'] = self.db_manager.fetchall()

            # Distribuição de entregas por dia da semana
            self.db_manager.execute(
                """
                SELECT strftime('%w', data_entrega) as dia_semana, COUNT(*) as total
                FROM comprovantes
                WHERE data_entrega BETWEEN ? AND ?
                GROUP BY dia_semana
                ORDER BY dia_semana
                """,
                (data_inicial, data_final)
            )
            dias_semana = {
                '0': 'Domingo',
                '1': 'Segunda',
                '2': 'Terça',
                '3': 'Quarta',
                '4': 'Quinta',
                '5': 'Sexta',
                '6': 'Sábado'
            }
            resultados = self.db_manager.fetchall()
            estatisticas['distribuicao_dia_semana'] = [(dias_semana[r[0]], r[1]) for r in resultados]

            self.logger.info("Estatísticas geradas com sucesso")
            return estatisticas

        except Exception as e:
            self.logger.error(f"Erro ao gerar estatísticas: {str(e)}")
            return {
                'total_parceiros': 0,
                'total_lojas': 0,
                'total_comprovantes': 0,
                'comprovantes_periodo': 0,
                'top_parceiros': [],
                'top_lojas': [],
                'distribuicao_dia_semana': []
            }