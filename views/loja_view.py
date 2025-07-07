#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Interface de Lojas
---------------------
Implementa a interface gráfica para o gerenciamento de lojas.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from controllers.loja_controller import LojaController
from utils.validators import formatar_cnpj, limpar_formatacao
from utils.tooltip import ToolTip

class LojaView(ttk.Frame):
    """Interface gráfica para gerenciamento de lojas."""

    def __init__(self, parent, db_manager):
        """
        Inicializa a interface de lojas.

        Args:
            parent (tk.Widget): Widget pai.
            db_manager (DatabaseManager): Instância do gerenciador de banco de dados.
        """
        super().__init__(parent)
        self.parent = parent
        self.logger = logging.getLogger(__name__)

        # Controlador
        self.controller = LojaController(db_manager)

        # ID da loja atual (para edição)
        self.loja_atual_id = None

        # Construir interface
        self._criar_widgets()
        self._configurar_eventos()

        # Carregar dados iniciais
        self._carregar_lojas()

    def _criar_widgets(self):
        """Cria os widgets da interface."""
        # Frame para formulário
        self.frame_form = ttk.LabelFrame(self, text="Cadastro de Lojas")
        self.frame_form.pack(fill=tk.X, padx=10, pady=10)

        # Campos do formulário
        # Linha 1
        ttk.Label(self.frame_form, text="Nome:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.entrada_nome = ttk.Entry(self.frame_form, width=40)
        self.entrada_nome.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.frame_form, text="CNPJ:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.entrada_cnpj = ttk.Entry(self.frame_form, width=20)
        self.entrada_cnpj.grid(row=0, column=3, padx=5, pady=5)

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

        # Linha 4
        ttk.Label(self.frame_form, text="Contato:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.entrada_contato = ttk.Entry(self.frame_form, width=40)
        self.entrada_contato.grid(row=3, column=1, padx=5, pady=5)

        # Linha 5
        ttk.Label(self.frame_form, text="Cidade:").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        self.entrada_cidade = ttk.Entry(self.frame_form, width=30)
        self.entrada_cidade.grid(row=4, column=1, padx=5, pady=5)

        ttk.Label(self.frame_form, text="Estado:").grid(row=4, column=2, padx=5, pady=5, sticky=tk.W)
        self.entrada_estado = ttk.Entry(self.frame_form, width=5)
        self.entrada_estado.grid(row=4, column=3, padx=5, pady=5, sticky=tk.W)

        # Linha 6
        ttk.Label(self.frame_form, text="Agrupamento:").grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)
        self.entrada_agrupamento = ttk.Entry(self.frame_form, width=20)
        self.entrada_agrupamento.grid(row=5, column=1, padx=5, pady=5, sticky=tk.W)

        # Frame para botões
        self.frame_botoes = ttk.Frame(self.frame_form)
        self.frame_botoes.grid(row=6, column=0, columnspan=4, pady=10)

        self.btn_adicionar = ttk.Button(self.frame_botoes, text="Adicionar", command=self._adicionar_loja)
        self.btn_adicionar.pack(side=tk.LEFT, padx=5)

        self.btn_editar = ttk.Button(self.frame_botoes, text="Salvar Edição",
                                     command=self._editar_loja, state=tk.DISABLED)
        self.btn_editar.pack(side=tk.LEFT, padx=5)

        self.btn_excluir = ttk.Button(self.frame_botoes, text="Excluir",
                                      command=self._excluir_loja, state=tk.DISABLED)
        self.btn_excluir.pack(side=tk.LEFT, padx=5)

        self.btn_limpar = ttk.Button(self.frame_botoes, text="Limpar", command=self._limpar_form)
        self.btn_limpar.pack(side=tk.LEFT, padx=5)

        # Frame para pesquisa
        self.frame_pesquisa = ttk.Frame(self)
        self.frame_pesquisa.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(self.frame_pesquisa, text="Pesquisar:").pack(side=tk.LEFT, padx=5)
        self.entrada_pesquisa = ttk.Entry(self.frame_pesquisa, width=40)
        self.entrada_pesquisa.pack(side=tk.LEFT, padx=5)

        self.btn_pesquisar = ttk.Button(self.frame_pesquisa, text="Buscar", command=self._pesquisar_loja)
        self.btn_pesquisar.pack(side=tk.LEFT, padx=5)

        self.btn_limpar_pesquisa = ttk.Button(self.frame_pesquisa, text="Limpar", command=self._limpar_pesquisa)
        self.btn_limpar_pesquisa.pack(side=tk.LEFT, padx=5)

        # Frame para listagem
        self.frame_lista = ttk.Frame(self)
        self.frame_lista.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Treeview para listagem
        colunas = (
            "id",
            "nome",
            "cnpj",
            "telefone",
            "email",
            "endereco",
            "contato",
            "cidade",
            "estado",
            "agrupamento",
            "data_cadastro",
        )
        self.treeview = ttk.Treeview(self.frame_lista, columns=colunas, show="headings", selectmode="browse")

        # Definir cabeçalhos
        self.treeview.heading("id", text="ID")
        self.treeview.heading("nome", text="Nome")
        self.treeview.heading("cnpj", text="CNPJ")
        self.treeview.heading("telefone", text="Telefone")
        self.treeview.heading("email", text="Email")
        self.treeview.heading("endereco", text="Endereço")
        self.treeview.heading("contato", text="Contato")
        self.treeview.heading("cidade", text="Cidade")
        self.treeview.heading("estado", text="Estado")
        self.treeview.heading("agrupamento", text="Agrupamento")
        self.treeview.heading("data_cadastro", text="Data de Cadastro")

        # Definir larguras das colunas
        self.treeview.column("id", width=50, minwidth=50)
        self.treeview.column("nome", width=200, minwidth=150)
        self.treeview.column("cnpj", width=120, minwidth=100)
        self.treeview.column("telefone", width=120, minwidth=100)
        self.treeview.column("email", width=180, minwidth=120)
        self.treeview.column("endereco", width=200, minwidth=150)
        self.treeview.column("contato", width=150, minwidth=100)
        self.treeview.column("cidade", width=120, minwidth=100)
        self.treeview.column("estado", width=60, minwidth=50)
        self.treeview.column("agrupamento", width=100, minwidth=80)
        self.treeview.column("data_cadastro", width=120, minwidth=100)

        # Scrollbar
        scrollbar = ttk.Scrollbar(self.frame_lista, orient=tk.VERTICAL, command=self.treeview.yview)
        self.treeview.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.treeview.pack(fill=tk.BOTH, expand=True)

        # Estilo zebra striping
        # Estilo zebra striping
        style = ttk.Style()
        style.map("Treeview", background=[("selected", "#347083")])
        style.configure("Treeview", rowheight=25)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.configure("Treeview", font=("Segoe UI", 10))

        self.treeview.tag_configure('oddrow', background='#f9f9f9')
        self.treeview.tag_configure('evenrow', background='#ffffff')

    def _configurar_eventos(self):
        """Configura os eventos da interface."""
        # Evento de seleção na treeview
        self.treeview.bind("<<TreeviewSelect>>", self._on_treeview_select)

        # Evento de tecla Enter na pesquisa
        self.entrada_pesquisa.bind("<Return>", lambda event: self._pesquisar_loja())

        # Formatação automática de CNPJ
        self.entrada_cnpj.bind("<FocusOut>", self._formatar_cnpj_entrada)

        # Teclas de atalho
        self.bind("<Escape>", lambda event: self._limpar_form())

    def _formatar_cnpj_entrada(self, event=None):
        """Formata o CNPJ na entrada quando o campo perde o foco."""
        cnpj = self.entrada_cnpj.get().strip()
        if cnpj:
            cnpj_formatado = formatar_cnpj(cnpj)
            self.entrada_cnpj.delete(0, tk.END)
            self.entrada_cnpj.insert(0, cnpj_formatado)

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
            self.loja_atual_id = valores[0]
            self.entrada_nome.insert(0, valores[1])
            self.entrada_cnpj.insert(0, valores[2] if valores[2] else "")
            self.entrada_telefone.insert(0, valores[3] if valores[3] else "")
            self.entrada_email.insert(0, valores[4] if valores[4] else "")
            self.entrada_endereco.insert(0, valores[5] if valores[5] else "")
            self.entrada_contato.insert(0, valores[6] if valores[6] else "")
            self.entrada_cidade.insert(0, valores[7] if valores[7] else "")
            self.entrada_estado.insert(0, valores[8] if valores[8] else "")
            self.entrada_agrupamento.insert(0, valores[9] if valores[9] else "")

            # Habilitar botões de edição e exclusão
            self.btn_editar.config(state=tk.NORMAL)
            self.btn_excluir.config(state=tk.NORMAL)

            # Desabilitar botão de adicionar
            self.btn_adicionar.config(state=tk.DISABLED)

            ToolTip(self.entrada_nome, "Digite o nome da loja.")
            ToolTip(self.entrada_cnpj, "Digite o CNPJ da loja (opcional).")
            ToolTip(self.entrada_telefone, "Digite o telefone de contato.")
            ToolTip(self.entrada_email, "Digite o e-mail da loja.")
            ToolTip(self.entrada_endereco, "Endereço completo da loja.")
            ToolTip(self.entrada_contato, "Nome da pessoa de contato.")
            ToolTip(self.entrada_cidade, "Cidade onde a loja está localizada.")
            ToolTip(self.entrada_estado, "Estado (UF) da loja, ex: SP, RJ.")
            ToolTip(self.entrada_agrupamento, "Identificador do agrupamento de lojas (opcional).")

            ToolTip(self.btn_adicionar, "Clique para adicionar uma nova loja.")
            ToolTip(self.btn_editar, "Clique para salvar alterações na loja selecionada.")
            ToolTip(self.btn_excluir, "Clique para excluir a loja selecionada.")
            ToolTip(self.btn_limpar, "Limpa os campos do formulário.")

            ToolTip(self.entrada_pesquisa, "Digite um termo para buscar por nome, CNPJ, cidade, etc.")
            ToolTip(self.btn_pesquisar, "Clique para buscar lojas conforme o termo digitado.")
            ToolTip(self.btn_limpar_pesquisa, "Limpa o campo de pesquisa e exibe todas as lojas.")

    def _obter_dados_form(self):
        """
        Obtém os dados do formulário.

        Returns:
            dict: Dicionário com os dados do formulário.
        """
        return {
            'nome': self.entrada_nome.get().strip(),
            'cnpj': limpar_formatacao(self.entrada_cnpj.get().strip()),
            'telefone': self.entrada_telefone.get().strip(),
            'email': self.entrada_email.get().strip(),
            'endereco': self.entrada_endereco.get().strip(),
            'contato': self.entrada_contato.get().strip(),
            'cidade': self.entrada_cidade.get().strip(),
            'estado': self.entrada_estado.get().strip(),
            'agrupamento_id': self.entrada_agrupamento.get().strip(),
        }

    def _limpar_form(self):
        """Limpa o formulário e reseta o estado dos botões."""
        # Limpar campos
        self.entrada_nome.delete(0, tk.END)
        self.entrada_cnpj.delete(0, tk.END)
        self.entrada_telefone.delete(0, tk.END)
        self.entrada_email.delete(0, tk.END)
        self.entrada_endereco.delete(0, tk.END)
        self.entrada_contato.delete(0, tk.END)
        self.entrada_cidade.delete(0, tk.END)
        self.entrada_estado.delete(0, tk.END)
        self.entrada_agrupamento.delete(0, tk.END)

        # Resetar ID atual
        self.loja_atual_id = None

        # Resetar estado dos botões
        self.btn_adicionar.config(state=tk.NORMAL)
        self.btn_editar.config(state=tk.DISABLED)
        self.btn_excluir.config(state=tk.DISABLED)

        # Limpar seleção da treeview
        for item in self.treeview.selection():
            self.treeview.selection_remove(item)
    
    def _adicionar_loja(self):
        """Adiciona uma nova loja."""
        # Obter dados do formulário
        dados = self._obter_dados_form()

        # Validar e adicionar
        sucesso, mensagem = self.controller.adicionar_loja(dados)

        if sucesso:
            messagebox.showinfo("Sucesso", mensagem)
            self._limpar_form()
            self._carregar_lojas()
        else:
            messagebox.showerror("Erro", mensagem)

    def _editar_loja(self):
        """Edita a loja selecionada."""
        if not self.loja_atual_id:
            messagebox.showwarning("Aviso", "Nenhuma loja selecionada para edição!")
            return

        # Obter dados do formulário
        dados = self._obter_dados_form()

        # Validar e editar
        sucesso, mensagem = self.controller.editar_loja(self.loja_atual_id, dados)

        if sucesso:
            messagebox.showinfo("Sucesso", mensagem)
            self._limpar_form()
            self._carregar_lojas()
        else:
            messagebox.showerror("Erro", mensagem)

    def _excluir_loja(self):
        """Exclui a loja selecionada."""
        if not self.loja_atual_id:
            messagebox.showwarning("Aviso", "Nenhuma loja selecionada para exclusão!")
            return

        # Confirmar exclusão
        nome = self.entrada_nome.get().strip()
        confirmacao = messagebox.askyesno("Confirmar Exclusão",
                                          f"Tem certeza que deseja excluir a loja '{nome}'?")

        if confirmacao:
            # Excluir loja
            sucesso, mensagem = self.controller.excluir_loja(self.loja_atual_id)

            if sucesso:
                messagebox.showinfo("Sucesso", mensagem)
                self._limpar_form()
                self._carregar_lojas()
            else:
                messagebox.showerror("Erro", mensagem)

    def _pesquisar_loja(self):
        """Pesquisa lojas pelo termo informado."""
        termo = self.entrada_pesquisa.get().strip()

        if not termo:
            self._carregar_lojas()
            return

        # Realizar pesquisa
        lojas = self.controller.pesquisar_lojas(termo)

        # Atualizar treeview
        self._atualizar_treeview(lojas)

    def _limpar_pesquisa(self):
        """Limpa o campo de pesquisa e recarrega todas as lojas."""
        self.entrada_pesquisa.delete(0, tk.END)
        self._carregar_lojas()

    def _carregar_lojas(self):
        """Carrega todas as lojas na treeview."""
        lojas = self.controller.listar_lojas()
        self._atualizar_treeview(lojas)

    def _atualizar_treeview(self, lojas):
        """
        Atualiza a treeview com as lojas fornecidas.

        Args:
            lojas (list): Lista de tuplas com os dados das lojas.
        """
        # Limpar treeview
        for item in self.treeview.get_children():
            self.treeview.delete(item)

        # Adicionar lojas à treeview
        for loja in lojas:
            # Formatar CNPJ para exibição
            cnpj_formatado = formatar_cnpj(loja[2]) if loja[2] else ""

            valores = (
                loja[0],  # id
                loja[1],  # nome
                cnpj_formatado,  # cnpj formatado
                loja[3],  # telefone
                loja[4],  # email
                loja[5],  # endereco
                loja[6],  # contato
                loja[8],  # cidade
                loja[9],  # estado
                loja[10],  # agrupamento
                loja[7],   # data_cadastro
            )

            tag = 'evenrow' if index % 2 == 0 else 'oddrow'
            self.treeview.insert("", "end", values=valores, tags=(tag,))

    def focus_nome(self):
        """Coloca o foco no campo de nome."""
        self.entrada_nome.focus_set()