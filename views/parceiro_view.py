#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Interface de Parceiros
---------------------
Implementa a interface gráfica para o gerenciamento de parceiros.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from controllers.parceiro_controller import ParceiroController
from utils.validators import formatar_cpf, limpar_formatacao


class ParceiroView(ttk.Frame):
    """Interface gráfica para gerenciamento de parceiros."""

    def __init__(self, parent, db_manager):
        """
        Inicializa a interface de parceiros.

        Args:
            parent (tk.Widget): Widget pai.
            db_manager (DatabaseManager): Instância do gerenciador de banco de dados.
        """
        super().__init__(parent)
        self.parent = parent
        self.logger = logging.getLogger(__name__)

        # Controlador
        self.controller = ParceiroController(db_manager)

        # ID do parceiro atual (para edição)
        self.parceiro_atual_id = None

        # Construir interface
        self._criar_widgets()
        self._configurar_eventos()

        # Carregar dados iniciais
        self._carregar_parceiros()

    def _criar_widgets(self):
        """Cria os widgets da interface."""
        # Frame para formulário
        self.frame_form = ttk.LabelFrame(self, text="Cadastro de Parceiros")
        self.frame_form.pack(fill=tk.X, padx=10, pady=10)

        # Campos do formulário
        # Linha 1
        ttk.Label(self.frame_form, text="Nome:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.entrada_nome = ttk.Entry(self.frame_form, width=40)
        self.entrada_nome.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.frame_form, text="CPF:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.entrada_cpf = ttk.Entry(self.frame_form, width=20)
        self.entrada_cpf.grid(row=0, column=3, padx=5, pady=5)

        # Linha 2
        ttk.Label(self.frame_form, text="Telefone:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.entrada_telefone = ttk.Entry(self.frame_form, width=20)
        self.entrada_telefone.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self.frame_form, text="Email:").grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)
        self.entrada_email = ttk.Entry(self.frame_form, width=30)
        self.entrada_email.grid(row=1, column=3, padx=5, pady=5)

        # Linha 3
        ttk.Label(self.frame_form, text="Endereço:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.entrada_endereco = ttk.Entry(self.frame_form, width=60)
        self.entrada_endereco.grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky=tk.EW)

        # Frame para botões
        self.frame_botoes = ttk.Frame(self.frame_form)
        self.frame_botoes.grid(row=3, column=0, columnspan=4, pady=10)

        self.btn_adicionar = ttk.Button(self.frame_botoes, text="Adicionar", command=self._adicionar_parceiro)
        self.btn_adicionar.pack(side=tk.LEFT, padx=5)

        self.btn_editar = ttk.Button(self.frame_botoes, text="Salvar Edição",
                                     command=self._editar_parceiro, state=tk.DISABLED)
        self.btn_editar.pack(side=tk.LEFT, padx=5)

        self.btn_excluir = ttk.Button(self.frame_botoes, text="Excluir",
                                      command=self._excluir_parceiro, state=tk.DISABLED)
        self.btn_excluir.pack(side=tk.LEFT, padx=5)

        self.btn_limpar = ttk.Button(self.frame_botoes, text="Limpar", command=self._limpar_form)
        self.btn_limpar.pack(side=tk.LEFT, padx=5)

        # Frame para pesquisa
        self.frame_pesquisa = ttk.Frame(self)
        self.frame_pesquisa.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(self.frame_pesquisa, text="Pesquisar:").pack(side=tk.LEFT, padx=5)
        self.entrada_pesquisa = ttk.Entry(self.frame_pesquisa, width=40)
        self.entrada_pesquisa.pack(side=tk.LEFT, padx=5)

        self.btn_pesquisar = ttk.Button(self.frame_pesquisa, text="Buscar", command=self._pesquisar_parceiro)
        self.btn_pesquisar.pack(side=tk.LEFT, padx=5)

        self.btn_limpar_pesquisa = ttk.Button(self.frame_pesquisa, text="Limpar", command=self._limpar_pesquisa)
        self.btn_limpar_pesquisa.pack(side=tk.LEFT, padx=5)

        # Frame para listagem
        self.frame_lista = ttk.Frame(self)
        self.frame_lista.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Treeview para listagem
        colunas = ("id", "nome", "cpf", "telefone", "email", "endereco", "data_cadastro")
        self.treeview = ttk.Treeview(self.frame_lista, columns=colunas, show="headings", selectmode="browse")

        # Definir cabeçalhos
        self.treeview.heading("id", text="ID")
        self.treeview.heading("nome", text="Nome")
        self.treeview.heading("cpf", text="CPF")
        self.treeview.heading("telefone", text="Telefone")
        self.treeview.heading("email", text="Email")
        self.treeview.heading("endereco", text="Endereço")
        self.treeview.heading("data_cadastro", text="Data de Cadastro")

        # Definir larguras das colunas
        self.treeview.column("id", width=50, minwidth=50)
        self.treeview.column("nome", width=200, minwidth=150)
        self.treeview.column("cpf", width=120, minwidth=100)
        self.treeview.column("telefone", width=120, minwidth=100)
        self.treeview.column("email", width=180, minwidth=120)
        self.treeview.column("endereco", width=250, minwidth=150)
        self.treeview.column("data_cadastro", width=120, minwidth=100)

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
        self.entrada_pesquisa.bind("<Return>", lambda event: self._pesquisar_parceiro())

        # Formatação automática de CPF
        self.entrada_cpf.bind("<FocusOut>", self._formatar_cpf_entrada)

        # Teclas de atalho
        self.bind("<Escape>", lambda event: self._limpar_form())

    def _formatar_cpf_entrada(self, event=None):
        """Formata o CPF na entrada quando o campo perde o foco."""
        cpf = self.entrada_cpf.get().strip()
        if cpf:
            cpf_formatado = formatar_cpf(cpf)
            self.entrada_cpf.delete(0, tk.END)
            self.entrada_cpf.insert(0, cpf_formatado)

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
            self.parceiro_atual_id = valores[0]
            self.entrada_nome.insert(0, valores[1])
            self.entrada_cpf.insert(0, valores[2] if valores[2] else "")
            self.entrada_telefone.insert(0, valores[3] if valores[3] else "")
            self.entrada_email.insert(0, valores[4] if valores[4] else "")
            self.entrada_endereco.insert(0, valores[5] if valores[5] else "")

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
        return {
            'nome': self.entrada_nome.get().strip(),
            'cpf': limpar_formatacao(self.entrada_cpf.get().strip()),
            'telefone': self.entrada_telefone.get().strip(),
            'email': self.entrada_email.get().strip(),
            'endereco': self.entrada_endereco.get().strip()
        }

    def _limpar_form(self):
        """Limpa o formulário e reseta o estado dos botões."""
        # Limpar campos
        self.entrada_nome.delete(0, tk.END)
        self.entrada_cpf.delete(0, tk.END)
        self.entrada_telefone.delete(0, tk.END)
        self.entrada_email.delete(0, tk.END)
        self.entrada_endereco.delete(0, tk.END)

        # Resetar ID atual
        self.parceiro_atual_id = None

        # Resetar estado dos botões
        self.btn_adicionar.config(state=tk.NORMAL)
        self.btn_editar.config(state=tk.DISABLED)
        self.btn_excluir.config(state=tk.DISABLED)

        # Limpar seleção da treeview
        for item in self.treeview.selection():
            self.treeview.selection_remove(item)

    def _adicionar_parceiro(self):
        """Adiciona um novo parceiro."""
        # Obter dados do formulário
        dados = self._obter_dados_form()

        # Validar e adicionar
        sucesso, mensagem = self.controller.adicionar_parceiro(dados)

        if sucesso:
            messagebox.showinfo("Sucesso", mensagem)
            self._limpar_form()
            self._carregar_parceiros()
        else:
            messagebox.showerror("Erro", mensagem)

    def _editar_parceiro(self):
        """Edita o parceiro selecionado."""
        if not self.parceiro_atual_id:
            messagebox.showwarning("Aviso", "Nenhum parceiro selecionado para edição!")
            return

        # Obter dados do formulário
        dados = self._obter_dados_form()

        # Validar e editar
        sucesso, mensagem = self.controller.editar_parceiro(self.parceiro_atual_id, dados)

        if sucesso:
            messagebox.showinfo("Sucesso", mensagem)
            self._limpar_form()
            self._carregar_parceiros()
        else:
            messagebox.showerror("Erro", mensagem)

    def _excluir_parceiro(self):
        """Exclui o parceiro selecionado."""
        if not self.parceiro_atual_id:
            messagebox.showwarning("Aviso", "Nenhum parceiro selecionado para exclusão!")
            return

        # Confirmar exclusão
        nome = self.entrada_nome.get().strip()
        confirmacao = messagebox.askyesno("Confirmar Exclusão",
                                          f"Tem certeza que deseja excluir o parceiro '{nome}'?")

        if confirmacao:
            # Excluir parceiro
            sucesso, mensagem = self.controller.excluir_parceiro(self.parceiro_atual_id)

            if sucesso:
                messagebox.showinfo("Sucesso", mensagem)
                self._limpar_form()
                self._carregar_parceiros()
            else:
                messagebox.showerror("Erro", mensagem)

    def _pesquisar_parceiro(self):
        """Pesquisa parceiros pelo termo informado."""
        termo = self.entrada_pesquisa.get().strip()

        if not termo:
            self._carregar_parceiros()
            return

        # Realizar pesquisa
        parceiros = self.controller.pesquisar_parceiros(termo)

        # Atualizar treeview
        self._atualizar_treeview(parceiros)

    def _limpar_pesquisa(self):
        """Limpa o campo de pesquisa e recarrega todos os parceiros."""
        self.entrada_pesquisa.delete(0, tk.END)
        self._carregar_parceiros()

    def _carregar_parceiros(self):
        """Carrega todos os parceiros na treeview."""
        parceiros = self.controller.listar_parceiros()
        self._atualizar_treeview(parceiros)

    def _atualizar_treeview(self, parceiros):
        """
        Atualiza a treeview com os parceiros fornecidos.

        Args:
            parceiros (list): Lista de tuplas com os dados dos parceiros.
        """
        # Limpar treeview
        for item in self.treeview.get_children():
            self.treeview.delete(item)

        # Adicionar parceiros à treeview
        for parceiro in parceiros:
            # Formatar CPF para exibição
            cpf_formatado = formatar_cpf(parceiro[2]) if parceiro[2] else ""

            valores = (
                parceiro[0],  # id
                parceiro[1],  # nome
                cpf_formatado,  # cpf formatado
                parceiro[3],  # telefone
                parceiro[4],  # email
                parceiro[5],  # endereco
                parceiro[6]  # data_cadastro
            )

            self.treeview.insert("", "end", values=valores)

    def focus_nome(self):
        """Coloca o foco no campo de nome."""
        self.entrada_nome.focus_set()