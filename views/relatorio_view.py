#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Interface de Relatórios
---------------------
Implementa a interface gráfica para geração e visualização de relatórios.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import logging
import datetime
from tkcalendar import DateEntry
import pandas as pd
from controllers.relatorio_controller import RelatorioController
from utils.validators import formatar_cpf
from utils.tooltip import ToolTip
from utils.style import configurar_estilos_modernos


class RelatorioView(ttk.Frame):
    """Interface gráfica para geração e visualização de relatórios."""

    def __init__(self, parent, db_manager):
        """
        Inicializa a interface de relatórios.

        Args:
            parent (tk.Widget): Widget pai.
            db_manager (DatabaseManager): Instância do gerenciador de banco de dados.
        """
        super().__init__(parent)
        self.parent = parent
        self.logger = logging.getLogger(__name__)
        self.parent = parent
        self.logger = logging.getLogger(__name__)
        configurar_estilos_modernos()

        # Controlador
        self.controller = RelatorioController(db_manager)

        # Construir interface
        self._criar_widgets()
        self._configurar_eventos()

    def _criar_widgets(self):
        """Cria os widgets da interface."""
        # Frame para seleção de tipo de relatório
        self.frame_tipo = ttk.LabelFrame(self, text="Tipo de Relatório")
        self.frame_tipo.pack(fill=tk.X, padx=10, pady=10)

        # Radiobuttons para seleção de tipo
        self.tipo_relatorio = tk.StringVar(value="parceiro")
        ttk.Radiobutton(
            self.frame_tipo,
            text="Relatório por Parceiro",
            variable=self.tipo_relatorio,
            value="parceiro",
            command=self._atualizar_filtros
        ).grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)

        ttk.Radiobutton(
            self.frame_tipo,
            text="Relatório por Loja",
            variable=self.tipo_relatorio,
            value="loja",
            command=self._atualizar_filtros
        ).grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)

        ttk.Radiobutton(
            self.frame_tipo,
            text="Relatório por Período",
            variable=self.tipo_relatorio,
            value="periodo",
            command=self._atualizar_filtros
        ).grid(row=0, column=2, padx=10, pady=5, sticky=tk.W)

        # Frame para filtros
        self.frame_filtros = ttk.LabelFrame(self, text="Filtros")
        self.frame_filtros.pack(fill=tk.X, padx=10, pady=10)

        # Filtro de parceiro
        ttk.Label(self.frame_filtros, text="Parceiro:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.combo_parceiro = ttk.Combobox(self.frame_filtros, width=40, state="readonly")
        self.combo_parceiro.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        # Filtro de loja
        ttk.Label(self.frame_filtros, text="Loja:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.combo_loja = ttk.Combobox(self.frame_filtros, width=40, state="readonly")
        self.combo_loja.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        # Filtro de período
        ttk.Label(self.frame_filtros, text="Data Inicial:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.data_inicial = DateEntry(
            self.frame_filtros,
            width=12,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            date_pattern='dd/mm/yyyy'
        )
        self.data_inicial.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

        ttk.Label(self.frame_filtros, text="Data Final:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.data_final = DateEntry(
            self.frame_filtros,
            width=12,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            date_pattern='dd/mm/yyyy'
        )
        self.data_final.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)

        # Definir data inicial para o primeiro dia do mês atual
        hoje = datetime.datetime.now()
        primeiro_dia = datetime.datetime(hoje.year, hoje.month, 1)
        self.data_inicial.set_date(primeiro_dia)

        # Frame para botões
        self.frame_botoes = ttk.Frame(self.frame_filtros)
        self.frame_botoes.grid(row=4, column=0, columnspan=2, pady=10)

        self.btn_gerar = ttk.Button(self.frame_botoes, text="Gerar Relatório", command=self._gerar_relatorio)
        self.btn_gerar.pack(side=tk.LEFT, padx=5)

        self.btn_excel = ttk.Button(self.frame_botoes, text="Exportar para Excel",
                                    command=self._exportar_excel, state=tk.DISABLED)
        self.btn_excel.pack(side=tk.LEFT, padx=5)

        self.btn_pdf = ttk.Button(self.frame_botoes, text="Exportar para PDF",
                                  command=self._exportar_pdf, state=tk.DISABLED)
        self.btn_pdf.pack(side=tk.LEFT, padx=5)

        self.btn_limpar = ttk.Button(self.frame_botoes, text="Limpar", command=self._limpar_filtros)
        self.btn_limpar.pack(side=tk.LEFT, padx=5)

        # Frame para resultados
        self.frame_resultados = ttk.LabelFrame(self, text="Resultados")
        self.frame_resultados.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Treeview para resultados
        colunas = ("id", "parceiro", "loja", "data_entrega", "comprovante", "observacoes")
        self.treeview = ttk.Treeview(self.frame_resultados, columns=colunas, show="headings", selectmode="browse")

        # Definir cabeçalhos
        self.treeview.heading("id", text="ID")
        self.treeview.heading("parceiro", text="Parceiro")
        self.treeview.heading("loja", text="Loja")
        self.treeview.heading("data_entrega", text="Data Entrega")
        self.treeview.heading("comprovante", text="Comprovante")
        self.treeview.heading("observacoes", text="Observações")

        # Definir larguras das colunas
        self.treeview.column("id", width=50, minwidth=50)
        self.treeview.column("parceiro", width=200, minwidth=150)
        self.treeview.column("loja", width=200, minwidth=150)
        self.treeview.column("data_entrega", width=120, minwidth=100)
        self.treeview.column("comprovante", width=150, minwidth=100)
        self.treeview.column("observacoes", width=250, minwidth=150)

        # Scrollbar
        scrollbar = ttk.Scrollbar(self.frame_resultados, orient=tk.VERTICAL, command=self.treeview.yview)
        self.treeview.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.treeview.pack(fill=tk.BOTH, expand=True)

        # Frame para resumo
        self.frame_resumo = ttk.LabelFrame(self, text="Resumo")
        self.frame_resumo.pack(fill=tk.X, padx=10, pady=10)

        # Labels para resumo
        ttk.Label(self.frame_resumo, text="Total de Entregas:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.lbl_total_entregas = ttk.Label(self.frame_resumo, text="0")
        self.lbl_total_entregas.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        ttk.Label(self.frame_resumo, text="Parceiros Envolvidos:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.lbl_total_parceiros = ttk.Label(self.frame_resumo, text="0")
        self.lbl_total_parceiros.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)

        ttk.Label(self.frame_resumo, text="Lojas Atendidas:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.lbl_total_lojas = ttk.Label(self.frame_resumo, text="0")
        self.lbl_total_lojas.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        ttk.Label(self.frame_resumo, text="Período:").grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)
        self.lbl_periodo = ttk.Label(self.frame_resumo, text="N/A")
        self.lbl_periodo.grid(row=1, column=3, padx=5, pady=5, sticky=tk.W)

        # Estilo zebra striping
        style = ttk.Style()
        style.map("Treeview", background=[("selected", "#347083")])
        style.configure("Treeview", rowheight=25)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.configure("Treeview", font=("Segoe UI", 10))

        self.treeview.tag_configure('oddrow', background='#f9f9f9')
        self.treeview.tag_configure('evenrow', background='#ffffff')

        # Armazenar os dados atuais para exportação
        self.dados_atuais = []

        # Preencher comboboxes
        self._carregar_parceiros_lojas()
        self._atualizar_filtros()

    def _configurar_eventos(self):
        """Configura os eventos da interface."""
        # Evento de seleção na treeview
        self.treeview.bind("<Double-1>", self._visualizar_comprovante)

        # Configurar atalhos
        self.bind("<F5>", lambda event: self._gerar_relatorio())
        self.bind("<Control-e>", lambda event: self._exportar_excel())
        self.bind("<Control-p>", lambda event: self._exportar_pdf())

    def _carregar_parceiros_lojas(self):
        """Carrega parceiros e lojas nas comboboxes."""
        # Carregar parceiros
        parceiros = self.controller.obter_parceiros_combobox()
        self.combo_parceiro['values'] = ["Todos os Parceiros"] + list(parceiros.keys())
        self.combo_parceiro.current(0)

        # Carregar lojas
        lojas = self.controller.obter_lojas_combobox()
        self.combo_loja['values'] = ["Todas as Lojas"] + list(lojas.keys())
        self.combo_loja.current(0)

    def _atualizar_filtros(self):
        """Atualiza a visibilidade dos filtros conforme o tipo de relatório."""
        tipo = self.tipo_relatorio.get()

        # Resetar estados
        self.combo_parceiro.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        self.combo_loja.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        self.data_inicial.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        self.data_final.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)

        # Configurar conforme o tipo
        if tipo == "parceiro":
            self.combo_parceiro.config(state="readonly")
            self.combo_loja.config(state="readonly")
        elif tipo == "loja":
            self.combo_parceiro.config(state="readonly")
            self.combo_loja.config(state="readonly")
        elif tipo == "periodo":
            self.combo_parceiro.config(state="readonly")
            self.combo_loja.config(state="readonly")

    def _gerar_relatorio(self):
        """Gera o relatório conforme os filtros selecionados."""
        try:
            # Obter valores dos filtros
            tipo = self.tipo_relatorio.get()
            parceiro = self.combo_parceiro.get() if self.combo_parceiro.get() != "Todos os Parceiros" else None
            loja = self.combo_loja.get() if self.combo_loja.get() != "Todas as Lojas" else None
            data_inicial = self.data_inicial.get_date()
            data_final = self.data_final.get_date()

            # Verificar se a data final é posterior à data inicial
            if data_final < data_inicial:
                messagebox.showerror("Erro", "A data final deve ser posterior à data inicial.")
                return

            # Converter datas para string no formato YYYY-MM-DD
            data_inicial_str = data_inicial.strftime("%Y-%m-%d")
            data_final_str = data_final.strftime("%Y-%m-%d")

            # Gerar relatório
            if tipo == "parceiro":
                titulo = f"Relatório de Entregas por Parceiro"
                if parceiro:
                    titulo += f" - {parceiro}"
                resultados = self.controller.gerar_relatorio_parceiro(parceiro, data_inicial_str, data_final_str, loja)
            elif tipo == "loja":
                titulo = f"Relatório de Entregas por Loja"
                if loja:
                    titulo += f" - {loja}"
                resultados = self.controller.gerar_relatorio_loja(loja, data_inicial_str, data_final_str, parceiro)
            elif tipo == "periodo":
                titulo = f"Relatório de Entregas por Período"
                resultados = self.controller.gerar_relatorio_periodo(data_inicial_str, data_final_str, parceiro, loja)

            # Atualizar título do frame de resultados
            self.frame_resultados.config(text=titulo)

            # Atualizar treeview
            self._atualizar_treeview(resultados)

            # Atualizar resumo
            self._atualizar_resumo(resultados, data_inicial_str, data_final_str)

            # Habilitar botões de exportação
            self.btn_excel.config(state=tk.NORMAL)
            self.btn_pdf.config(state=tk.NORMAL)

            # Armazenar resultados para exportação
            self.dados_atuais = resultados

            self.logger.info(f"Relatório gerado: {titulo}")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar relatório: {str(e)}")
            self.logger.error(f"Erro ao gerar relatório: {str(e)}")

    def _atualizar_treeview(self, resultados):
        """
        Atualiza a treeview com os resultados do relatório.

        Args:
            resultados (list): Lista de tuplas com os dados dos comprovantes.
        """
        # Limpar treeview
        for item in self.treeview.get_children():
            self.treeview.delete(item)

        # Adicionar resultados à treeview
        for index, resultado in enumerate(resultados):
            valores = (
                resultado[0],  # id
                resultado[1],  # parceiro
                resultado[2],  # loja
                resultado[3],  # data_entrega
                resultado[4],  # comprovante
                resultado[5] if len(resultado) > 5 else ""  # observacoes
            )
            tag = 'evenrow' if index % 2 == 0 else 'oddrow'
            self.treeview.insert("", "end", values=valores, tags=(tag,))

    def _atualizar_resumo(self, resultados, data_inicial, data_final):
        """
        Atualiza as informações de resumo do relatório.

        Args:
            resultados (list): Lista de tuplas com os dados dos comprovantes.
            data_inicial (str): Data inicial do período no formato YYYY-MM-DD.
            data_final (str): Data final do período no formato YYYY-MM-DD.
        """
        # Calcular totais
        total_entregas = len(resultados)

        # Obter parceiros e lojas únicos
        parceiros = set()
        lojas = set()
        for resultado in resultados:
            parceiros.add(resultado[1])  # parceiro
            lojas.add(resultado[2])  # loja

        total_parceiros = len(parceiros)
        total_lojas = len(lojas)

        # Formatar datas para exibição
        data_inicial_formatada = datetime.datetime.strptime(data_inicial, "%Y-%m-%d").strftime("%d/%m/%Y")
        data_final_formatada = datetime.datetime.strptime(data_final, "%Y-%m-%d").strftime("%d/%m/%Y")
        periodo = f"{data_inicial_formatada} a {data_final_formatada}"

        # Atualizar labels
        self.lbl_total_entregas.config(text=str(total_entregas))
        self.lbl_total_parceiros.config(text=str(total_parceiros))
        self.lbl_total_lojas.config(text=str(total_lojas))
        self.lbl_periodo.config(text=periodo)

    def _limpar_filtros(self):
        """Limpa os filtros do relatório."""
        # Resetar comboboxes
        self.combo_parceiro.current(0)
        self.combo_loja.current(0)

        # Resetar datas
        hoje = datetime.datetime.now()
        primeiro_dia = datetime.datetime(hoje.year, hoje.month, 1)
        self.data_inicial.set_date(primeiro_dia)
        self.data_final.set_date(hoje)

        # Limpar treeview
        for item in self.treeview.get_children():
            self.treeview.delete(item)

        # Resetar resumo
        self.lbl_total_entregas.config(text="0")
        self.lbl_total_parceiros.config(text="0")
        self.lbl_total_lojas.config(text="0")
        self.lbl_periodo.config(text="N/A")

        # Desabilitar botões de exportação
        self.btn_excel.config(state=tk.DISABLED)
        self.btn_pdf.config(state=tk.DISABLED)

        # Resetar título
        self.frame_resultados.config(text="Resultados")

        # Limpar dados atuais
        self.dados_atuais = []

    def _exportar_excel(self):
        """Exporta os resultados para um arquivo Excel."""
        if not self.dados_atuais:
            messagebox.showwarning("Aviso", "Não há dados para exportar.")
            return

        try:
            # Solicitar local para salvar o arquivo
            tipo = self.tipo_relatorio.get()
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"relatorio_{tipo}_{timestamp}.xlsx"

            filepath = filedialog.asksaveasfilename(
                title="Exportar para Excel",
                initialfile=default_filename,
                defaultextension=".xlsx",
                filetypes=[("Arquivos Excel", "*.xlsx"), ("Todos os Arquivos", "*.*")]
            )

            if not filepath:
                return  # Usuário cancelou

            # Preparar dados para o DataFrame
            dados = []
            for resultado in self.dados_atuais:
                dados.append({
                    "ID": resultado[0],
                    "Parceiro": resultado[1],
                    "Loja": resultado[2],
                    "Data Entrega": resultado[3],
                    "Comprovante": resultado[4],
                    "Observações": resultado[5] if len(resultado) > 5 else ""
                })

            # Criar DataFrame
            df = pd.DataFrame(dados)

            # Adicionar informações de cabeçalho
            data_inicial_formatada = self.data_inicial.get_date().strftime("%d/%m/%Y")
            data_final_formatada = self.data_final.get_date().strftime("%d/%m/%Y")

            # Exportar para Excel
            with pd.ExcelWriter(filepath, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name='Relatório', index=False, startrow=2)

                # Obter workbook e worksheet
                workbook = writer.book
                worksheet = writer.sheets['Relatório']

                # Formatar cabeçalho
                header_format = workbook.add_format({
                    'bold': True,
                    'text_wrap': True,
                    'valign': 'top',
                    'fg_color': '#D7E4BC',
                    'border': 1
                })

                # Adicionar título
                titulo = f"Relatório de Entregas - {self.frame_resultados.cget('text')}"
                subtitulo = f"Período: {data_inicial_formatada} a {data_final_formatada}"

                worksheet.write(0, 0, titulo)
                worksheet.write(1, 0, subtitulo)

                # Aplicar formatação nos cabeçalhos
                for col_num, value in enumerate(df.columns.values):
                    worksheet.write(2, col_num, value, header_format)

                # Ajustar largura das colunas
                worksheet.set_column('A:A', 10)  # ID
                worksheet.set_column('B:B', 30)  # Parceiro
                worksheet.set_column('C:C', 30)  # Loja
                worksheet.set_column('D:D', 15)  # Data Entrega
                worksheet.set_column('E:E', 30)  # Comprovante
                worksheet.set_column('F:F', 40)  # Observações

            messagebox.showinfo("Exportação Concluída", f"Dados exportados com sucesso para:\n{filepath}")
            self.logger.info(f"Relatório exportado para Excel: {filepath}")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar para Excel: {str(e)}")
            self.logger.error(f"Erro ao exportar para Excel: {str(e)}")

    def _exportar_pdf(self):
        """Exporta os resultados para um arquivo PDF."""
        if not self.dados_atuais:
            messagebox.showwarning("Aviso", "Não há dados para exportar.")
            return

        try:
            # Solicitar local para salvar o arquivo
            tipo = self.tipo_relatorio.get()
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"relatorio_{tipo}_{timestamp}.pdf"

            filepath = filedialog.asksaveasfilename(
                title="Exportar para PDF",
                initialfile=default_filename,
                defaultextension=".pdf",
                filetypes=[("Arquivos PDF", "*.pdf"), ("Todos os Arquivos", "*.*")]
            )

            if not filepath:
                return  # Usuário cancelou

            # Preparar dados para o DataFrame
            dados = []
            for resultado in self.dados_atuais:
                dados.append({
                    "ID": resultado[0],
                    "Parceiro": resultado[1],
                    "Loja": resultado[2],
                    "Data Entrega": resultado[3],
                    "Comprovante": resultado[4],
                    "Observações": resultado[5] if len(resultado) > 5 else ""
                })

            # Criar DataFrame
            df = pd.DataFrame(dados)

            # Importar módulos necessários
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4, landscape
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet

            # Configurar documento
            doc = SimpleDocTemplate(filepath, pagesize=landscape(A4))
            elements = []

            # Estilos
            styles = getSampleStyleSheet()
            title_style = styles['Title']
            subtitle_style = styles['Heading2']
            normal_style = styles['Normal']

            # Adicionar título
            titulo = f"Relatório de Entregas - {self.frame_resultados.cget('text')}"
            elements.append(Paragraph(titulo, title_style))
            elements.append(Spacer(1, 12))

            # Adicionar subtítulo
            data_inicial_formatada = self.data_inicial.get_date().strftime("%d/%m/%Y")
            data_final_formatada = self.data_final.get_date().strftime("%d/%m/%Y")
            subtitulo = f"Período: {data_inicial_formatada} a {data_final_formatada}"
            elements.append(Paragraph(subtitulo, subtitle_style))
            elements.append(Spacer(1, 12))

            # Adicionar resumo
            elementos_resumo = [
                [Paragraph("Total de Entregas:", normal_style),
                 Paragraph(self.lbl_total_entregas.cget("text"), normal_style)],
                [Paragraph("Parceiros Envolvidos:", normal_style),
                 Paragraph(self.lbl_total_parceiros.cget("text"), normal_style)],
                [Paragraph("Lojas Atendidas:", normal_style),
                 Paragraph(self.lbl_total_lojas.cget("text"), normal_style)],
            ]

            table_resumo = Table(elementos_resumo, colWidths=[120, 80])
            table_resumo.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))

            elements.append(table_resumo)
            elements.append(Spacer(1, 24))

            # Adicionar tabela de dados
            # Preparar dados
            data = [df.columns.tolist()] + df.values.tolist()

            # Criar tabela
            table = Table(data, repeatRows=1)

            # Estilo da tabela
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
            ]))

            elements.append(table)

            # Gerar PDF
            doc.build(elements)

            messagebox.showinfo("Exportação Concluída", f"Dados exportados com sucesso para:\n{filepath}")
            self.logger.info(f"Relatório exportado para PDF: {filepath}")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar para PDF: {str(e)}")
            self.logger.error(f"Erro ao exportar para PDF: {str(e)}")

    def _visualizar_comprovante(self, event=None):
        """Visualiza o comprovante da entrega selecionada."""
        try:
            # Obter item selecionado
            selecao = self.treeview.selection()
            if not selecao:
                return

            # Obter dados do item selecionado
            item = self.treeview.item(selecao[0])
            valores = item["values"]

            # Obter ID do comprovante
            comprovante_id = valores[0]

            # Solicitar visualização ao controlador
            self.controller.visualizar_comprovante(comprovante_id)

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao visualizar comprovante: {str(e)}")
            self.logger.error(f"Erro ao visualizar comprovante: {str(e)}")

    def selecionar_tipo(self, tipo):
        """
        Seleciona o tipo de relatório.

        Args:
            tipo (str): Tipo de relatório ('parceiro', 'loja' ou 'periodo').
        """
        if tipo in ['parceiro', 'loja', 'periodo']:
            self.tipo_relatorio.set(tipo)
            self._atualizar_filtros()
            self._limpar_filtros()
            self.logger.info(f"Tipo de relatório alterado para: {tipo}")