#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Interface de Associações
----------------------
Implementa a interface gráfica para o gerenciamento de associações entre parceiros e lojas.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from controllers.associacao_controller import AssociacaoController
from utils import carregar_combobox_por_cidade

class AssociacaoView(ttk.Frame):
    """Interface gráfica para gerenciamento de associações entre parceiros e lojas."""

    def __init__(self, parent, db_manager):
        """
        Inicializa a interface de associações.

        Args:
            parent (tk.Widget): Widget pai.
            db_manager (DatabaseManager): Instância do gerenciador de banco de dados.
        """
        super().__init__(parent)
        self.parent = parent
        self.logger = logging.getLogger(__name__)

        # Controlador
        self.controller = AssociacaoController(db_manager)

        # ID da associação atual (para edição)
        self.associacao_atual_id = None

        # Dicionários para mapear nomes para IDs
        self.parceiros = {}
        self.lojas = {}

        # Construir interface
        self._criar_widgets()
        self._configurar_eventos()

        # Carregar dados iniciais
        self._carregar_parceiros()
        self._carregar_lojas()
        self._carregar_associacoes()

    def _criar_widgets(self):
        """Cria os widgets da interface."""
        # Frame para formulário
        self.frame_form = ttk.LabelFrame(self, text="Associação de Parceiros e Lojas")
        self.frame_form.pack(fill=tk.X, padx=10, pady=10)

        # Campos do formulário
        # Linha 1
        ttk.Label(self.frame_form, text="Parceiro:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.combo_parceiro = ttk.Combobox(self.frame_form, width=40, state="readonly")
        self.combo_parceiro.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.frame_form, text="Loja:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.combo_loja = ttk.Combobox(self.frame_form, width=40, state="readonly")
        self.combo_loja.grid(row=0, column=3, padx=5, pady=5)

        # Linha 2
        ttk.Label(self.frame_form, text="Status:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.combo_status = ttk.Combobox(self.frame_form, width=20, state="readonly")
        self.combo_status.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        self.combo_status['values'] = ('Ativo', 'Inativo', 'Pendente')
        self.combo_status.current(0)

        ttk.Label(self.frame_form, text="Observações:").grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)
        self.entrada_observacao = ttk.Entry(self.frame_form, width=40)
        self.entrada_observacao.grid(row=1, column=3, padx=5, pady=5)

        # Frame para botões
        self.frame_botoes = ttk.Frame(self.frame_form)
        self.frame_botoes.grid(row=2, column=0, columnspan=4, pady=10)

        self.btn_adicionar = ttk.Button(self.frame_botoes, text="Associar", command=self._adicionar_associacao)
        self.btn_adicionar.pack(side=tk.LEFT, padx=5)

        self.btn_editar = ttk.Button(self.frame_botoes, text="Salvar Edição",
                                     command=self._editar_associacao, state=tk.DISABLED)
        self.btn_editar.pack(side=tk.LEFT, padx=5)

        self.btn_excluir = ttk.Button(self.frame_botoes, text="Excluir",
                                      command=self._excluir_associacao, state=tk.DISABLED)
        self.btn_excluir.pack(side=tk.LEFT, padx=5)

        self.btn_limpar = ttk.Button(self.frame_botoes, text="Limpar", command=self._limpar_form)
        self.btn_limpar.pack(side=tk.LEFT, padx=5)

        # Frame para pesquisa
        self.frame_pesquisa = ttk.Frame(self)
        self.frame_pesquisa.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(self.frame_pesquisa, text="Pesquisar:").pack(side=tk.LEFT, padx=5)
        self.entrada_pesquisa = ttk.Entry(self.frame_pesquisa, width=40)
        self.entrada_pesquisa.pack(side=tk.LEFT, padx=5)

        self.btn_pesquisar = ttk.Button(self.frame_pesquisa, text="Buscar", command=self._pesquisar_associacao)
        self.btn_pesquisar.pack(side=tk.LEFT, padx=5)

        self.btn_limpar_pesquisa = ttk.Button(self.frame_pesquisa, text="Limpar", command=self._limpar_pesquisa)
        self.btn_limpar_pesquisa.pack(side=tk.LEFT, padx=5)

        # Frame para filtros
        self.frame_filtros = ttk.Frame(self)
        self.frame_filtros.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(self.frame_filtros, text="Filtrar por:").pack(side=tk.LEFT, padx=5)
        self.combo_filtro_parceiro = ttk.Combobox(self.frame_filtros, width=30, state="readonly")
        self.combo_filtro_parceiro.pack(side=tk.LEFT, padx=5)
        self.combo_filtro_parceiro.bind("<<ComboboxSelected>>", self._filtrar_associacoes)

        self.combo_filtro_loja = ttk.Combobox(self.frame_filtros, width=30, state="readonly")
        self.combo_filtro_loja.pack(side=tk.LEFT, padx=5)
        self.combo_filtro_loja.bind("<<ComboboxSelected>>", self._filtrar_associacoes)

        self.combo_filtro_status = ttk.Combobox(self.frame_filtros, width=15, state="readonly")
        self.combo_filtro_status.pack(side=tk.LEFT, padx=5)
        self.combo_filtro_status['values'] = ('Todos', 'Ativo', 'Inativo', 'Pendente')
        self.combo_filtro_status.current(0)
        self.combo_filtro_status.bind("<<ComboboxSelected>>", self._filtrar_associacoes)

        self.btn_limpar_filtros = ttk.Button(self.frame_filtros, text="Limpar Filtros", command=self._limpar_filtros)
        self.btn_limpar_filtros.pack(side=tk.LEFT, padx=5)

        # Frame para listagem
        self.frame_lista = ttk.Frame(self)
        self.frame_lista.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Treeview para listagem
        colunas = ("id", "parceiro", "loja", "status", "observacao", "data_associacao")
        self.treeview = ttk.Treeview(self.frame_lista, columns=colunas, show="headings", selectmode="browse")

        # Definir cabeçalhos
        self.treeview.heading("id", text="ID")
        self.treeview.heading("parceiro", text="Parceiro")
        self.treeview.heading("loja", text="Loja")
        self.treeview.heading("status", text="Status")
        self.treeview.heading("observacao", text="Observações")
        self.treeview.heading("data_associacao", text="Data da Associação")

        # Definir larguras das colunas
        self.treeview.column("id", width=50, minwidth=50)
        self.treeview.column("parceiro", width=200, minwidth=150)
        self.treeview.column("loja", width=200, minwidth=150)
        self.treeview.column("status", width=100, minwidth=80)
        self.treeview.column("observacao", width=250, minwidth=150)
        self.treeview.column("data_associacao", width=150, minwidth=120)

        # Scrollbar
        scrollbar = ttk.Scrollbar(self.frame_lista, orient=tk.VERTICAL, command=self.treeview.yview)
        self.treeview.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.treeview.pack(fill=tk.BOTH, expand=True)

    def _configurar_eventos(self):
        """Configura os eventos da interface."""
        # Evento de seleção na treeview
        self.treeview.bind("<<TreeviewSelect>>", self._on_treeview_select)

        # Evento de tecla Enter na pesquisa
        self.entrada_pesquisa.bind("<Return>", lambda event: self._pesquisar_associacao())

        # Combobox dinâmico por cidade
        self.combo_parceiro.bind("<<ComboboxSelected>>", self._on_parceiro_change)
        self.combo_loja.bind("<<ComboboxSelected>>", self._on_loja_change)

        # Teclas de atalho
        self.bind("<Escape>", lambda event: self._limpar_form())

    def _carregar_parceiros(self):
        """Carrega os parceiros para o combobox."""
        try:
            # Obter lista de parceiros do controlador
            self.parceiros = self.controller.obter_parceiros_combobox()

            # Atualizar combobox de parceiros
            self.combo_parceiro['values'] = list(self.parceiros.keys())

            # Atualizar combobox de filtro de parceiros
            filtro_values = ["Todos os Parceiros"]
            filtro_values.extend(list(self.parceiros.keys()))
            self.combo_filtro_parceiro['values'] = filtro_values
            self.combo_filtro_parceiro.current(0)

            self.logger.debug(f"Parceiros carregados: {len(self.parceiros)}")
        except Exception as e:
            self.logger.error(f"Erro ao carregar parceiros: {str(e)}")
            messagebox.showerror("Erro", f"Erro ao carregar parceiros: {str(e)}")

    def _carregar_lojas(self):
        """Carrega as lojas para o combobox."""
        try:
            # Obter lista de lojas do controlador␊
            self.lojas = self.controller.obter_lojas_combobox()

            # Atualizar combobox de lojas
            self.combo_loja['values'] = list(self.lojas.keys())

            # Atualizar combobox de filtro de lojas
            filtro_values = ["Todas as Lojas"]
            filtro_values.extend(list(self.lojas.keys()))
            self.combo_filtro_loja['values'] = filtro_values
            self.combo_filtro_loja.current(0)

            self.logger.debug(f"Lojas carregadas: {len(self.lojas)}")
        except Exception as e:
            self.logger.error(f"Erro ao carregar lojas: {str(e)}")
            messagebox.showerror("Erro", f"Erro ao carregar lojas: {str(e)}")

    def _on_parceiro_change(self, event=None):
        """Filtra as lojas pela cidade do parceiro selecionado."""
        parceiro_nome = self.combo_parceiro.get()
        parceiro_id = self.parceiros.get(parceiro_nome)
        if parceiro_id:
            parceiro = self.controller.parceiro_controller.obter_parceiro(parceiro_id)
            if parceiro and parceiro.get("cidade"):
                self.lojas = carregar_combobox_por_cidade(
                    self.controller.db_manager, "lojas", parceiro["cidade"]
                )
                self.combo_loja["values"] = list(self.lojas.keys())

    def _on_loja_change(self, event=None):
        """Filtra os parceiros pela cidade da loja selecionada."""
        loja_nome = self.combo_loja.get()
        loja_id = self.lojas.get(loja_nome)
        if loja_id:
            loja = self.controller.loja_controller.obter_loja(loja_id)
            if loja and loja.get("cidade"):
                self.parceiros = carregar_combobox_por_cidade(
                    self.controller.db_manager, "parceiros", loja["cidade"]
                )
                self.combo_parceiro["values"] = list(self.parceiros.keys())

    def _on_treeview_select(self, event=None):
        """Manipula o evento de seleção na treeview."""
        selecao = self.treeview.selection()
        if selecao:
            # Obter dados da linha selecionada
            item = self.treeview.item(selecao[0])
            valores = item["values"]

            # Limpar formulário
            self._limpar_form()

            # Preencher formulário com dados selecionados
            self.associacao_atual_id = valores[0]

            # Selecionar parceiro e loja nos comboboxes
            parceiro_nome = valores[1]
            loja_nome = valores[2]

            # Encontrar índices nos comboboxes
            try:
                parceiro_index = list(self.parceiros.keys()).index(parceiro_nome)
                self.combo_parceiro.current(parceiro_index)
            except ValueError:
                self.logger.warning(f"Parceiro não encontrado no combo: {parceiro_nome}")

            try:
                loja_index = list(self.lojas.keys()).index(loja_nome)
                self.combo_loja.current(loja_index)
            except ValueError:
                self.logger.warning(f"Loja não encontrada no combo: {loja_nome}")

            # Configurar status
            status = valores[3]
            if status in self.combo_status['values']:
                self.combo_status.set(status)

            # Configurar observação
            self.entrada_observacao.insert(0, valores[4] if valores[4] else "")

            # Habilitar botões de edição e exclusão
            self.btn_editar.config(state=tk.NORMAL)
            self.btn_excluir.config(state=tk.NORMAL)

            # Desabilitar botão de adicionar
            self.btn_adicionar.config(state=tk.DISABLED)

    def _obter_dados_form(self):
        """
        Obtém os dados do formulário.

        Returns:
            dict: Dicionário com os dados do formulário.
        """
        # Obter parceiro selecionado
        parceiro_nome = self.combo_parceiro.get()
        parceiro_id = self.parceiros.get(parceiro_nome)

        # Obter loja selecionada
        loja_nome = self.combo_loja.get()
        loja_id = self.lojas.get(loja_nome)

        return {
            'parceiro_id': parceiro_id,
            'loja_id': loja_id,
            'status': self.combo_status.get(),
            'observacao': self.entrada_observacao.get().strip()
        }

    def _limpar_form(self):
        """Limpa o formulário e reseta o estado dos botões."""
        # Limpar campos
        if self.combo_parceiro['values']:
            self.combo_parceiro.set('')
        if self.combo_loja['values']:
            self.combo_loja.set('')
        self.combo_status.current(0)
        self.entrada_observacao.delete(0, tk.END)

        # Resetar ID atual
        self.associacao_atual_id = None

        # Resetar estado dos botões
        self.btn_adicionar.config(state=tk.NORMAL)
        self.btn_editar.config(state=tk.DISABLED)
        self.btn_excluir.config(state=tk.DISABLED)

        # Limpar seleção da treeview
        for item in self.treeview.selection():
            self.treeview.selection_remove(item)

    def _adicionar_associacao(self):
        """Adiciona uma nova associação."""
        # Obter dados do formulário
        dados = self._obter_dados_form()

        # Validar seleção de parceiro e loja
        if not dados['parceiro_id']:
            messagebox.showwarning("Aviso", "Selecione um parceiro!")
            return

        if not dados['loja_id']:
            messagebox.showwarning("Aviso", "Selecione uma loja!")
            return

        # Validar e adicionar
        sucesso, mensagem = self.controller.adicionar_associacao(dados)

        if sucesso:
            messagebox.showinfo("Sucesso", mensagem)
            self._limpar_form()
            self._carregar_associacoes()
        else:
            messagebox.showerror("Erro", mensagem)

    def _editar_associacao(self):
        """Edita a associação selecionada."""
        if not self.associacao_atual_id:
            messagebox.showwarning("Aviso", "Nenhuma associação selecionada para edição!")
            return

        # Obter dados do formulário
        dados = self._obter_dados_form()

        # Validar seleção de parceiro e loja
        if not dados['parceiro_id']:
            messagebox.showwarning("Aviso", "Selecione um parceiro!")
            return

        if not dados['loja_id']:
            messagebox.showwarning("Aviso", "Selecione uma loja!")
            return

        # Validar e editar
        sucesso, mensagem = self.controller.editar_associacao(self.associacao_atual_id, dados)

        if sucesso:
            messagebox.showinfo("Sucesso", mensagem)
            self._limpar_form()
            self._carregar_associacoes()
        else:
            messagebox.showerror("Erro", mensagem)

    def _excluir_associacao(self):
        """Exclui a associação selecionada."""
        if not self.associacao_atual_id:
            messagebox.showwarning("Aviso", "Nenhuma associação selecionada para exclusão!")
            return

        # Confirmar exclusão
        parceiro_nome = self.combo_parceiro.get()
        loja_nome = self.combo_loja.get()
        confirmacao = messagebox.askyesno("Confirmar Exclusão",
                                          f"Tem certeza que deseja excluir a associação entre o parceiro '{parceiro_nome}' e a loja '{loja_nome}'?")

        if confirmacao:
            # Excluir associação
            sucesso, mensagem = self.controller.excluir_associacao(self.associacao_atual_id)

            if sucesso:
                messagebox.showinfo("Sucesso", mensagem)
                self._limpar_form()
                self._carregar_associacoes()
            else:
                messagebox.showerror("Erro", mensagem)

    def _pesquisar_associacao(self):
        """Pesquisa associações pelo termo informado."""
        termo = self.entrada_pesquisa.get().strip()

        if not termo:
            self._carregar_associacoes()
            return

        # Realizar pesquisa
        associacoes = self.controller.pesquisar_associacoes(termo)

        # Atualizar treeview
        self._atualizar_treeview(associacoes)

    def _limpar_pesquisa(self):
        """Limpa o campo de pesquisa e recarrega todas as associações."""
        self.entrada_pesquisa.delete(0, tk.END)
        self._carregar_associacoes()

    def _filtrar_associacoes(self, event=None):
        """Filtra as associações com base nos filtros selecionados."""
        filtro_parceiro = self.combo_filtro_parceiro.get()
        filtro_loja = self.combo_filtro_loja.get()
        filtro_status = self.combo_filtro_status.get()

        # Obter IDs de filtro
        parceiro_id = None
        if filtro_parceiro != "Todos os Parceiros":
            parceiro_id = self.parceiros.get(filtro_parceiro)

        loja_id = None
        if filtro_loja != "Todas as Lojas":
            loja_id = self.lojas.get(filtro_loja)

        status = None
        if filtro_status != "Todos":
            status = filtro_status

        # Aplicar filtros
        associacoes = self.controller.filtrar_associacoes(parceiro_id, loja_id, status)

        # Atualizar treeview
        self._atualizar_treeview(associacoes)

    def _limpar_filtros(self):
        """Limpa os filtros e recarrega todas as associações."""
        self.combo_filtro_parceiro.current(0)
        self.combo_filtro_loja.current(0)
        self.combo_filtro_status.current(0)
        self._carregar_associacoes()

    def _carregar_associacoes(self):
        """Carrega todas as associações na treeview."""
        associacoes = self.controller.listar_associacoes()
        self._atualizar_treeview(associacoes)

    def _atualizar_treeview(self, associacoes):
        """
        Atualiza a treeview com as associações fornecidas.

        Args:
            associacoes (list): Lista de tuplas com os dados das associações.
        """
        # Limpar treeview
        for item in self.treeview.get_children():
            self.treeview.delete(item)

        # Adicionar associações à treeview
        for associacao in associacoes:
            valores = (
                associacao[0],  # id
                associacao[1],  # parceiro_nome
                associacao[2],  # loja_nome
                associacao[3],  # status
                associacao[4],  # observacao
                associacao[5]  # data_associacao
            )

            self.treeview.insert("", "end", values=valores)

    def focus_parceiro(self):
        """Coloca o foco no combobox de parceiros."""
        self.combo_parceiro.focus_set()