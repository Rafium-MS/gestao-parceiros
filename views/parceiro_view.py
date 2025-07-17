#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Interface de Parceiros - Versão Melhorada
-----------------------------------------
Implementa a interface gráfica moderna para o gerenciamento de parceiros.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from controllers.parceiro_controller import ParceiroController
from utils.validators import formatar_cpf, limpar_formatacao
from utils.tooltip import ToolTip
from utils.style import configurar_estilos_modernos

class ParceiroView(ttk.Frame):
    """Interface gráfica moderna para gerenciamento de parceiros."""

    def __init__(self, parent, db_manager):
        super().__init__(parent)
        self.parent = parent
        self.logger = logging.getLogger(__name__)
        self.controller = ParceiroController(db_manager)
        self.parceiro_atual_id = None
        self.produtos_adicionados = []

        self._criar_widgets()
        self._configurar_eventos()
        self._carregar_parceiros()

    def _configurar_estilos(self):
        """Configura estilos personalizados para a interface."""
        configurar_estilos_modernos()

    def _criar_widgets(self):
        """Cria os widgets da interface com layout moderno."""
        # Container principal com padding
        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # ==================== SEÇÃO SUPERIOR ====================
        top_section = ttk.Frame(main_container)
        top_section.pack(fill=tk.X, pady=(0, 20))

        # Título da seção
        title_label = ttk.Label(top_section, text="Gerenciamento de Parceiros",
                                font=("Segoe UI", 16, "bold"))
        title_label.pack(anchor=tk.W, pady=(0, 10))

        # Barra de pesquisa moderna
        search_frame = ttk.Frame(top_section)
        search_frame.pack(fill=tk.X, pady=(0, 15))

        search_label = ttk.Label(search_frame, text="🔍 Buscar Parceiro:",
                                 font=("Segoe UI", 10))
        search_label.pack(side=tk.LEFT, padx=(0, 10))

        self.entrada_pesquisa = ttk.Entry(search_frame, style="Modern.TEntry",
                                          font=("Segoe UI", 10), width=40)
        self.entrada_pesquisa.pack(side=tk.LEFT, padx=(0, 10))

        self.btn_pesquisar = ttk.Button(search_frame, text="Buscar",
                                        style="Action.TButton",
                                        command=self._pesquisar_parceiro)
        self.btn_pesquisar.pack(side=tk.LEFT, padx=(0, 5))

        self.btn_limpar_pesquisa = ttk.Button(search_frame, text="Limpar",
                                              style="Action.TButton",
                                              command=self._limpar_pesquisa)
        self.btn_limpar_pesquisa.pack(side=tk.LEFT)

        # ==================== FORMULÁRIO ====================
        form_container = ttk.Frame(main_container)
        form_container.pack(fill=tk.X, pady=(0, 20))

        # Informações Pessoais
        self.frame_info = ttk.LabelFrame(form_container, text="📋 Informações Pessoais",
                                         style="Card.TLabelframe", padding=(15, 10))
        self.frame_info.pack(fill=tk.X, pady=(0, 10))

        # Grid para informações pessoais
        info_grid = ttk.Frame(self.frame_info)
        info_grid.pack(fill=tk.X)

        # Linha 1
        ttk.Label(info_grid, text="Nome Completo *:", style="Bold.TLabel").grid(
            row=0, column=0, padx=(0, 10), pady=(0, 10), sticky=tk.W)
        self.entrada_nome = ttk.Entry(info_grid, style="Modern.TEntry",
                                      font=("Segoe UI", 10), width=35)
        self.entrada_nome.grid(row=0, column=1, padx=(0, 20), pady=(0, 10), sticky=tk.EW)

        ttk.Label(info_grid, text="CPF/CNPJ:", style="Bold.TLabel").grid(
            row=0, column=2, padx=(0, 10), pady=(0, 10), sticky=tk.W)
        self.entrada_cpf = ttk.Entry(info_grid, style="Modern.TEntry",
                                     font=("Segoe UI", 10), width=18)
        self.entrada_cpf.grid(row=0, column=3, pady=(0, 10), sticky=tk.EW)

        # Linha 2
        ttk.Label(info_grid, text="Telefone:", style="Bold.TLabel").grid(
            row=1, column=0, padx=(0, 10), pady=(0, 10), sticky=tk.W)
        self.entrada_telefone = ttk.Entry(info_grid, style="Modern.TEntry",
                                          font=("Segoe UI", 10), width=18)
        self.entrada_telefone.grid(row=1, column=1, padx=(0, 20), pady=(0, 10), sticky=tk.W)

        ttk.Label(info_grid, text="Email:", style="Bold.TLabel").grid(
            row=1, column=2, padx=(0, 10), pady=(0, 10), sticky=tk.W)
        self.entrada_email = ttk.Entry(info_grid, style="Modern.TEntry",
                                       font=("Segoe UI", 10), width=25)
        self.entrada_email.grid(row=1, column=3, pady=(0, 10), sticky=tk.EW)

        # Linha 3
        ttk.Label(info_grid, text="Endereço:", style="Bold.TLabel").grid(
            row=2, column=0, padx=(0, 10), pady=(0, 10), sticky=tk.W)
        self.entrada_endereco = ttk.Entry(info_grid, style="Modern.TEntry",
                                          font=("Segoe UI", 10))
        self.entrada_endereco.grid(row=2, column=1, columnspan=3, padx=(0, 0),
                                   pady=(0, 10), sticky=tk.EW)

        # Linha 4
        ttk.Label(info_grid, text="Cidade:", style="Bold.TLabel").grid(
            row=3, column=0, padx=(0, 10), pady=(0, 10), sticky=tk.W)
        self.entrada_cidade = ttk.Entry(info_grid, style="Modern.TEntry",
                                        font=("Segoe UI", 10), width=25)
        self.entrada_cidade.grid(row=3, column=1, padx=(0, 20), pady=(0, 10), sticky=tk.EW)

        ttk.Label(info_grid, text="Estado:", style="Bold.TLabel").grid(
            row=3, column=2, padx=(0, 10), pady=(0, 10), sticky=tk.W)
        self.entrada_estado = ttk.Entry(info_grid, style="Modern.TEntry",
                                        font=("Segoe UI", 10), width=5)
        self.entrada_estado.grid(row=3, column=3, pady=(0, 10), sticky=tk.W)

        # Configurar pesos das colunas
        info_grid.columnconfigure(1, weight=1)
        info_grid.columnconfigure(3, weight=1)

        # Informações Bancárias
        self.frame_financeiro = ttk.LabelFrame(form_container, text="💳 Informações Bancárias",
                                               style="Card.TLabelFrame", padding=(15, 10))
        self.frame_financeiro.pack(fill=tk.X, pady=(0, 10))

        # Grid para informações bancárias
        bank_grid = ttk.Frame(self.frame_financeiro)
        bank_grid.pack(fill=tk.X)

        # Linha 1
        ttk.Label(bank_grid, text="Banco:", style="Bold.TLabel").grid(
            row=0, column=0, padx=(0, 10), pady=(0, 10), sticky=tk.W)
        self.entrada_banco = ttk.Entry(bank_grid, style="Modern.TEntry",
                                       font=("Segoe UI", 10), width=25)
        self.entrada_banco.grid(row=0, column=1, padx=(0, 20), pady=(0, 10), sticky=tk.EW)

        ttk.Label(bank_grid, text="Agência:", style="Bold.TLabel").grid(
            row=0, column=2, padx=(0, 10), pady=(0, 10), sticky=tk.W)
        self.entrada_agencia = ttk.Entry(bank_grid, style="Modern.TEntry",
                                         font=("Segoe UI", 10), width=12)
        self.entrada_agencia.grid(row=0, column=3, padx=(0, 20), pady=(0, 10), sticky=tk.W)

        ttk.Label(bank_grid, text="Conta:", style="Bold.TLabel").grid(
            row=0, column=4, padx=(0, 10), pady=(0, 10), sticky=tk.W)
        self.entrada_conta = ttk.Entry(bank_grid, style="Modern.TEntry",
                                       font=("Segoe UI", 10), width=18)
        self.entrada_conta.grid(row=0, column=5, pady=(0, 10), sticky=tk.EW)

        # Linha 2
        ttk.Label(bank_grid, text="Tipo:", style="Bold.TLabel").grid(
            row=1, column=0, padx=(0, 10), pady=(0, 10), sticky=tk.W)
        self.combo_tipo = ttk.Combobox(bank_grid, values=["Corrente", "Poupança", "Pix"],
                                       width=15, state="readonly", font=("Segoe UI", 10))
        self.combo_tipo.grid(row=1, column=1, pady=(0, 10), sticky=tk.W)

        # Configurar pesos das colunas
        bank_grid.columnconfigure(1, weight=1)
        bank_grid.columnconfigure(5, weight=1)

        # Produtos e Valores
        self.frame_produtos = ttk.LabelFrame(form_container, text="📦 Produtos e Valores",
                                             style="Card.TLabelFrame", padding=(15, 10))
        self.frame_produtos.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Entrada de produtos
        produto_input = ttk.Frame(self.frame_produtos)
        produto_input.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(produto_input, text="Produto:", style="Bold.TLabel").grid(
            row=0, column=0, padx=(0, 10), pady=5, sticky=tk.W)
        self.entrada_produto = ttk.Entry(produto_input, style="Modern.TEntry",
                                         font=("Segoe UI", 10), width=30)
        self.entrada_produto.grid(row=0, column=1, padx=(0, 20), pady=5, sticky=tk.EW)

        ttk.Label(produto_input, text="Valor (R$):", style="Bold.TLabel").grid(
            row=0, column=2, padx=(0, 10), pady=5, sticky=tk.W)
        self.entrada_valor = ttk.Entry(produto_input, style="Modern.TEntry",
                                       font=("Segoe UI", 10), width=15)
        self.entrada_valor.grid(row=0, column=3, padx=(0, 20), pady=5, sticky=tk.W)

        self.btn_add_produto = ttk.Button(produto_input, text="➕ Adicionar",
                                          style="Action.TButton",
                                          command=self._adicionar_produto)
        self.btn_add_produto.grid(row=0, column=4, pady=5)

        produto_input.columnconfigure(1, weight=1)

        # Lista de produtos
        self.tree_produtos = ttk.Treeview(self.frame_produtos,
                                          columns=("produto", "valor"),
                                          show="headings", height=4,
                                          style="Modern.Treeview")
        self.tree_produtos.heading("produto", text="Produto")
        self.tree_produtos.heading("valor", text="Valor Unitário")
        self.tree_produtos.column("produto", width=300)
        self.tree_produtos.column("valor", width=120)
        self.tree_produtos.pack(fill=tk.BOTH, expand=True)

        # ==================== BOTÕES DE AÇÃO ====================
        actions_frame = ttk.Frame(main_container)
        actions_frame.pack(fill=tk.X, pady=(0, 20))

        # Botões principais
        buttons_left = ttk.Frame(actions_frame)
        buttons_left.pack(side=tk.LEFT)

        self.btn_adicionar = ttk.Button(buttons_left, text="✅ Adicionar Parceiro",
                                        style="Primary.TButton",
                                        command=self._adicionar_parceiro)
        self.btn_adicionar.pack(side=tk.LEFT, padx=(0, 10))

        self.btn_editar = ttk.Button(buttons_left, text="💾 Salvar Alterações",
                                     style="Primary.TButton",
                                     command=self._editar_parceiro,
                                     state=tk.DISABLED)
        self.btn_editar.pack(side=tk.LEFT, padx=(0, 10))

        # Botões secundários
        buttons_right = ttk.Frame(actions_frame)
        buttons_right.pack(side=tk.RIGHT)

        self.btn_limpar = ttk.Button(buttons_right, text="🧹 Limpar",
                                     style="Action.TButton",
                                     command=self._limpar_form)
        self.btn_limpar.pack(side=tk.RIGHT, padx=(10, 0))

        self.btn_excluir = ttk.Button(buttons_right, text="🗑️ Excluir",
                                      style="Danger.TButton",
                                      command=self._excluir_parceiro,
                                      state=tk.DISABLED)
        self.btn_excluir.pack(side=tk.RIGHT, padx=(10, 0))

        # ==================== LISTA DE PARCEIROS ====================
        list_frame = ttk.LabelFrame(main_container, text="📋 Lista de Parceiros",
                                    style="Card.TLabelFrame", padding=(15, 10))
        list_frame.pack(fill=tk.BOTH, expand=True)

        # Treeview para listagem
        tree_frame = ttk.Frame(list_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        colunas = ("id", "nome", "cpf", "telefone", "email", "cidade", "estado", "data_cadastro")
        self.treeview = ttk.Treeview(tree_frame, columns=colunas, show="headings",
                                     selectmode="browse", style="Modern.Treeview")

        # Definir cabeçalhos
        headers = {
            "id": "ID",
            "nome": "Nome",
            "cpf": "CPF/CNPJ",
            "telefone": "Telefone",
            "email": "Email",
            "cidade": "Cidade",
            "estado": "UF",
            "data_cadastro": "Data Cadastro"
        }

        # Definir larguras das colunas
        widths = {
            "id": 60,
            "nome": 200,
            "cpf": 120,
            "telefone": 120,
            "email": 180,
            "cidade": 120,
            "estado": 60,
            "data_cadastro": 120
        }

        for col in colunas:
            self.treeview.heading(col, text=headers[col])
            self.treeview.column(col, width=widths[col], minwidth=50)

        # Scrollbars
        scrollbar_v = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.treeview.yview)
        scrollbar_h = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.treeview.xview)

        self.treeview.configure(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)

        # Layout das scrollbars
        self.treeview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_v.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_h.pack(side=tk.BOTTOM, fill=tk.X)

        # Tags para linhas alternadas
        self.treeview.tag_configure('oddrow', background='#f8f9fa')
        self.treeview.tag_configure('evenrow', background='#ffffff')

        # Tooltips
        self._adicionar_tooltips()

    def _adicionar_tooltips(self):
        """Adiciona tooltips aos elementos da interface."""
        ToolTip(self.entrada_nome, "Digite o nome completo do parceiro (obrigatório)")
        ToolTip(self.entrada_cpf, "CPF no formato 000.000.000-00 ou CNPJ (opcional)")
        ToolTip(self.entrada_telefone, "Telefone para contato")
        ToolTip(self.entrada_email, "Email para contato")
        ToolTip(self.entrada_endereco, "Endereço completo")
        ToolTip(self.entrada_cidade, "Cidade onde o parceiro está localizado")
        ToolTip(self.entrada_estado, "Estado (UF)")
        ToolTip(self.entrada_banco, "Nome do banco")
        ToolTip(self.entrada_agencia, "Número da agência")
        ToolTip(self.entrada_conta, "Número da conta")
        ToolTip(self.combo_tipo, "Tipo da conta bancária")
        ToolTip(self.entrada_produto, "Nome do produto ou serviço")
        ToolTip(self.entrada_valor, "Valor unitário do produto")
        ToolTip(self.btn_add_produto, "Adiciona o produto à lista")
        ToolTip(self.btn_adicionar, "Cadastra um novo parceiro")
        ToolTip(self.btn_editar, "Salva as alterações no parceiro selecionado")
        ToolTip(self.btn_excluir, "Remove o parceiro selecionado")
        ToolTip(self.btn_limpar, "Limpa todos os campos do formulário")
        ToolTip(self.entrada_pesquisa, "Digite nome, CPF ou cidade para buscar")

    def _configurar_eventos(self):
        """Configura os eventos da interface."""
        # Evento de seleção na treeview
        self.treeview.bind("<<TreeviewSelect>>", self._on_treeview_select)

        # Evento de duplo clique na treeview
        self.treeview.bind("<Double-1>", self._on_treeview_double_click)

        # Evento de tecla Enter na pesquisa
        self.entrada_pesquisa.bind("<Return>", lambda event: self._pesquisar_parceiro())

        # Formatação automática de CPF
        self.entrada_cpf.bind("<FocusOut>", self._formatar_cpf_entrada)

        # Validação numérica para valor
        self.entrada_valor.bind("<KeyRelease>", self._validar_valor)

        # Teclas de atalho
        self.bind("<Control-n>", lambda event: self._limpar_form())
        self.bind("<Control-s>", lambda event: self._salvar_parceiro())
        self.bind("<Delete>", lambda event: self._excluir_parceiro())
        self.bind("<Escape>", lambda event: self._limpar_form())

        # Remover produto da lista
        self.tree_produtos.bind("<Delete>", self._remover_produto)

    def _validar_valor(self, event=None):
        """Valida se o valor digitado é numérico."""
        valor = self.entrada_valor.get()
        if valor and not valor.replace('.', '').replace(',', '').isdigit():
            # Remove caracteres não numéricos
            novo_valor = ''.join(c for c in valor if c.isdigit() or c in '.,')
            self.entrada_valor.delete(0, tk.END)
            self.entrada_valor.insert(0, novo_valor)

    def _on_treeview_double_click(self, event=None):
        """Manipula o evento de duplo clique na treeview."""
        # Foca no primeiro campo para edição rápida
        self.entrada_nome.focus_set()
        self.entrada_nome.selection_range(0, tk.END)

    def _remover_produto(self, event=None):
        """Remove o produto selecionado da lista."""
        selecao = self.tree_produtos.selection()
        if selecao:
            item = self.tree_produtos.item(selecao[0])
            produto = item["values"][0]

            # Confirmar remoção
            if messagebox.askyesno("Confirmar", f"Remover o produto '{produto}'?"):
                # Remover da árvore
                self.tree_produtos.delete(selecao[0])

                # Remover da lista
                self.produtos_adicionados = [p for p in self.produtos_adicionados
                                             if p["produto"] != produto]

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
            self.entrada_cidade.insert(0, valores[5] if valores[5] else "")
            self.entrada_estado.insert(0, valores[6] if valores[6] else "")

            # Carregar produtos do parceiro (se houver)
            self._carregar_produtos_parceiro(self.parceiro_atual_id)

            # Habilitar botões de edição e exclusão
            self.btn_editar.config(state=tk.NORMAL)
            self.btn_excluir.config(state=tk.NORMAL)

            # Desabilitar botão de adicionar
            self.btn_adicionar.config(state=tk.DISABLED)

    def _carregar_produtos_parceiro(self, parceiro_id):
        """Carrega os produtos do parceiro selecionado."""
        # Limpar lista de produtos
        for item in self.tree_produtos.get_children():
            self.tree_produtos.delete(item)

        self.produtos_adicionados = []

        # Aqui você pode implementar a lógica para carregar produtos do banco
        # Por enquanto, vamos deixar vazio
        pass

    def _obter_dados_form(self):
        """Obtém os dados do formulário."""
        return {
            'nome': self.entrada_nome.get().strip(),
            'cpf': limpar_formatacao(self.entrada_cpf.get().strip()),
            'telefone': self.entrada_telefone.get().strip(),
            'email': self.entrada_email.get().strip(),
            'endereco': self.entrada_endereco.get().strip(),
            'cidade': self.entrada_cidade.get().strip(),
            'estado': self.entrada_estado.get().strip(),
            'banco': self.entrada_banco.get().strip(),
            'agencia': self.entrada_agencia.get().strip(),
            'conta': self.entrada_conta.get().strip(),
            'tipo': self.combo_tipo.get().strip(),
            'produtos': self.produtos_adicionados
        }

    def _limpar_form(self):
        """Limpa o formulário e reseta o estado dos botões."""
        # Limpar campos
        campos = [
            self.entrada_nome, self.entrada_cpf, self.entrada_telefone,
            self.entrada_email, self.entrada_endereco, self.entrada_cidade,
            self.entrada_estado, self.entrada_banco, self.entrada_agencia,
            self.entrada_conta, self.entrada_produto, self.entrada_valor
        ]

        for campo in campos:
            campo.delete(0, tk.END)

        self.combo_tipo.set("")

        # Limpar produtos
        for item in self.tree_produtos.get_children():
            self.tree_produtos.delete(item)

        self.produtos_adicionados = []

        # Resetar ID atual
        self.parceiro_atual_id = None

        # Resetar estado dos botões
        self.btn_adicionar.config(state=tk.NORMAL)
        self.btn_editar.config(state=tk.DISABLED)
        self.btn_excluir.config(state=tk.DISABLED)

        # Limpar seleção da treeview
        for item in self.treeview.selection():
            self.treeview.selection_remove(item)

    def _adicionar_produto(self):
        """Adiciona um produto à lista."""
        nome = self.entrada_produto.get().strip()
        valor = self.entrada_valor.get().strip()

        if not nome or not valor:
            messagebox.showwarning("Campos obrigatórios",
                                   "Informe o produto e o valor unitário.")
            return

        try:
            valor_float = float(valor.replace(',', '.'))
        except ValueError:
            messagebox.showerror("Valor inválido",
                                 "O valor deve ser numérico (use ponto ou vírgula para decimais).")
            return

        # Verificar se o produto já existe
        for produto in self.produtos_adicionados:
            if produto["produto"].lower() == nome.lower():
                messagebox.showwarning("Produto duplicado",
                                       f"O produto '{nome}' já está na lista.")
                return

        # Adicionar à árvore
        self.tree_produtos.insert("", "end", values=(nome, f"R$ {valor_float:.2f}"))

        # Adicionar à lista
        self.produtos_adicionados.append({"produto": nome, "valor": valor_float})

        # Limpar campos
        self.entrada_produto.delete(0, tk.END)
        self.entrada_valor.delete(0, tk.END)

        # Focar no campo produto
        self.entrada_produto.focus_set()

    def _salvar_parceiro(self):
        """Salva o parceiro (adicionar ou editar)."""
        if self.parceiro_atual_id:
            self._editar_parceiro()
        else:
            self._adicionar_parceiro()

    def _adicionar_parceiro(self):
        """Adiciona um novo parceiro."""
        # Obter dados do formulário
        dados = self._obter_dados_form()

        # Validar campos obrigatórios
        if not dados['nome']:
            messagebox.showerror("Campo obrigatório", "O campo Nome é obrigatório.")
            self.entrada_nome.focus_set()
            return

        # Validar e adicionar
        try:
            sucesso, mensagem = self.controller.adicionar_parceiro(dados)

            if sucesso:
                messagebox.showinfo("✅ Sucesso", mensagem)
                self._limpar_form()
                self._carregar_parceiros()

                # Sugerir lojas da cidade (se implementado)
                cidade = dados.get("cidade")
                if cidade and hasattr(self, 'loja_controller'):
                    self._sugerir_lojas_cidade(cidade)

            else:
                messagebox.showerror("❌ Erro", mensagem)

        except Exception as e:
            self.logger.error(f"Erro ao adicionar parceiro: {e}")
            messagebox.showerror("❌ Erro", f"Erro inesperado: {str(e)}")

    def _editar_parceiro(self):
        """Edita o parceiro selecionado."""
        if not self.parceiro_atual_id:
            messagebox.showwarning("⚠️ Aviso", "Nenhum parceiro selecionado para edição!")
            return

        # Obter dados do formulário
        dados = self._obter_dados_form()

        # Validar campos obrigatórios
        if not dados['nome']:
            messagebox.showerror("Campo obrigatório", "O campo Nome é obrigatório.")
            self.entrada_nome.focus_set()
            return

        # Validar e editar
        try:
            sucesso, mensagem = self.controller.editar_parceiro(self.parceiro_atual_id, dados)

            if sucesso:
                messagebox.showinfo("✅ Sucesso", mensagem)
                self._limpar_form()
                self._carregar_parceiros()

                # Sugerir lojas da cidade (se implementado)
                cidade = dados.get("cidade")
                if cidade and hasattr(self, 'loja_controller'):
                    self._sugerir_lojas_cidade(cidade)

            else:
                messagebox.showerror("❌ Erro", mensagem)

        except Exception as e:
            self.logger.error(f"Erro ao editar parceiro: {e}")
            messagebox.showerror("❌ Erro", f"Erro inesperado: {str(e)}")

    def _excluir_parceiro(self):
        """Exclui o parceiro selecionado."""
        if not self.parceiro_atual_id:
            messagebox.showwarning("⚠️ Aviso", "Nenhum parceiro selecionado para exclusão!")
            return

        # Confirmar exclusão
        nome = self.entrada_nome.get().strip()
        confirmacao = messagebox.askyesno("🗑️ Confirmar Exclusão",
                                          f"Tem certeza que deseja excluir o parceiro '{nome}'?\n\n"
                                          "Esta ação não pode ser desfeita.")

        if confirmacao:
            try:
                # Excluir parceiro
                sucesso, mensagem = self.controller.excluir_parceiro(self.parceiro_atual_id)

                if sucesso:
                    messagebox.showinfo("✅ Sucesso", mensagem)
                    self._limpar_form()
                    self._carregar_parceiros()
                else:
                    messagebox.showerror("❌ Erro", mensagem)

            except Exception as e:
                self.logger.error(f"Erro ao excluir parceiro: {e}")
                messagebox.showerror("❌ Erro", f"Erro inesperado: {str(e)}")

    def _sugerir_lojas_cidade(self, cidade):
        """Sugere lojas na cidade do parceiro."""
        try:
            lojas = self.loja_controller.obter_lojas_por_cidade(cidade)
            if lojas:
                nomes = "\n".join(f"• {loja['nome']}" for loja in lojas)
                messagebox.showinfo("🏪 Lojas Sugeridas",
                                    f"Lojas em {cidade} disponíveis para associação:\n\n{nomes}")
        except Exception as e:
            self.logger.warning(f"Erro ao sugerir lojas: {e}")

    def _pesquisar_parceiro(self):
        """Pesquisa parceiros pelo termo informado."""
        termo = self.entrada_pesquisa.get().strip()

        if not termo:
            self._carregar_parceiros()
            return

        try:
            # Realizar pesquisa
            parceiros = self.controller.pesquisar_parceiros(termo)

            # Atualizar treeview
            self._atualizar_treeview(parceiros)

            # Mostrar resultado da pesquisa
            if parceiros:
                messagebox.showinfo("🔍 Resultado da Pesquisa",
                                    f"Encontrados {len(parceiros)} parceiro(s) para '{termo}'")
            else:
                messagebox.showinfo("🔍 Resultado da Pesquisa",
                                    f"Nenhum parceiro encontrado para '{termo}'")

        except Exception as e:
            self.logger.error(f"Erro na pesquisa: {e}")
            messagebox.showerror("❌ Erro", f"Erro na pesquisa: {str(e)}")

    def _limpar_pesquisa(self):
        """Limpa o campo de pesquisa e recarrega todos os parceiros."""
        self.entrada_pesquisa.delete(0, tk.END)
        self._carregar_parceiros()

    def _carregar_parceiros(self):
        """Carrega todos os parceiros na treeview."""
        try:
            parceiros = self.controller.listar_parceiros()
            self._atualizar_treeview(parceiros)
        except Exception as e:
            self.logger.error(f"Erro ao carregar parceiros: {e}")
            messagebox.showerror("❌ Erro", f"Erro ao carregar parceiros: {str(e)}")

    def _atualizar_treeview(self, parceiros):
        """Atualiza a treeview com os parceiros fornecidos."""
        # Limpar treeview
        for item in self.treeview.get_children():
            self.treeview.delete(item)

        # Adicionar parceiros à treeview
        for index, parceiro in enumerate(parceiros):
            try:
                # Formatar CPF para exibição
                cpf_formatado = formatar_cpf(parceiro[2]) if parceiro[2] else ""

                # Formatar data se necessário
                data_cadastro = parceiro[7] if len(parceiro) > 7 else ""
                if data_cadastro and len(str(data_cadastro)) > 10:
                    data_cadastro = str(data_cadastro)[:10]

                valores = (
                    parceiro[0],  # id
                    parceiro[1],  # nome
                    cpf_formatado,  # cpf formatado
                    parceiro[3] if len(parceiro) > 3 else "",  # telefone
                    parceiro[4] if len(parceiro) > 4 else "",  # email
                    parceiro[6] if len(parceiro) > 6 else "",  # cidade
                    parceiro[7] if len(parceiro) > 7 else "",  # estado
                    data_cadastro,  # data_cadastro
                )

                # Alternar cores das linhas
                tag = 'evenrow' if index % 2 == 0 else 'oddrow'
                self.treeview.insert("", "end", values=valores, tags=(tag,))

            except Exception as e:
                self.logger.warning(f"Erro ao processar parceiro {parceiro}: {e}")
                continue

    def _exportar_dados(self):
        """Exporta os dados dos parceiros para CSV."""
        try:
            from tkinter import filedialog
            import csv
            from datetime import datetime

            # Selecionar arquivo
            arquivo = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Exportar Parceiros",
                initialvalue=f"parceiros_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            )

            if arquivo:
                parceiros = self.controller.listar_parceiros()

                with open(arquivo, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)

                    # Cabeçalho
                    writer.writerow(['ID', 'Nome', 'CPF', 'Telefone', 'Email',
                                     'Endereço', 'Cidade', 'Estado', 'Data Cadastro'])

                    # Dados
                    for parceiro in parceiros:
                        writer.writerow(parceiro[:9])  # Primeiros 9 campos

                messagebox.showinfo("✅ Exportação", f"Dados exportados com sucesso!\n{arquivo}")

        except Exception as e:
            self.logger.error(f"Erro na exportação: {e}")
            messagebox.showerror("❌ Erro", f"Erro na exportação: {str(e)}")

    def _imprimir_relatorio(self):
        """Gera um relatório dos parceiros para impressão."""
        try:
            from datetime import datetime
            import tempfile
            import os

            parceiros = self.controller.listar_parceiros()

            # Criar arquivo HTML temporário
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
                f.write(f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Relatório de Parceiros</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 20px; }}
                        h1 {{ color: #333; text-align: center; }}
                        .info {{ text-align: center; margin-bottom: 20px; color: #666; }}
                        table {{ width: 100%; border-collapse: collapse; }}
                        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                        th {{ background-color: #f2f2f2; font-weight: bold; }}
                        tr:nth-child(even) {{ background-color: #f9f9f9; }}
                        .total {{ margin-top: 20px; font-weight: bold; }}
                    </style>
                </head>
                <body>
                    <h1>Relatório de Parceiros</h1>
                    <div class="info">
                        Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}
                    </div>
                    <table>
                        <tr>
                            <th>ID</th>
                            <th>Nome</th>
                            <th>CPF</th>
                            <th>Telefone</th>
                            <th>Email</th>
                            <th>Cidade</th>
                            <th>Estado</th>
                        </tr>
                """)

                for parceiro in parceiros:
                    cpf_formatado = formatar_cpf(parceiro[2]) if parceiro[2] else ""
                    f.write(f"""
                        <tr>
                            <td>{parceiro[0]}</td>
                            <td>{parceiro[1]}</td>
                            <td>{cpf_formatado}</td>
                            <td>{parceiro[3] if len(parceiro) > 3 else ""}</td>
                            <td>{parceiro[4] if len(parceiro) > 4 else ""}</td>
                            <td>{parceiro[6] if len(parceiro) > 6 else ""}</td>
                            <td>{parceiro[7] if len(parceiro) > 7 else ""}</td>
                        </tr>
                    """)

                f.write(f"""
                    </table>
                    <div class="total">
                        Total de parceiros: {len(parceiros)}
                    </div>
                </body>
                </html>
                """)

                arquivo_temp = f.name

            # Abrir no navegador
            import webbrowser
            webbrowser.open(f'file://{arquivo_temp}')

            messagebox.showinfo("📄 Relatório", "Relatório gerado e aberto no navegador!")

        except Exception as e:
            self.logger.error(f"Erro ao gerar relatório: {e}")
            messagebox.showerror("❌ Erro", f"Erro ao gerar relatório: {str(e)}")

    def focus_nome(self):
        """Coloca o foco no campo de nome."""
        self.entrada_nome.focus_set()

    def obter_parceiro_selecionado(self):
        """Retorna os dados do parceiro selecionado."""
        if self.parceiro_atual_id:
            return self._obter_dados_form()
        return None

    def selecionar_parceiro(self, parceiro_id):
        """Seleciona um parceiro na lista pelo ID."""
        for item in self.treeview.get_children():
            valores = self.treeview.item(item)["values"]
            if valores[0] == parceiro_id:
                self.treeview.selection_set(item)
                self.treeview.focus(item)
                self.treeview.see(item)
                break

    def atualizar_dados(self):
        """Atualiza os dados da interface."""
        self._carregar_parceiros()

    def validar_formulario(self):
        """Valida os dados do formulário."""
        dados = self._obter_dados_form()

        if not dados['nome']:
            return False, "O campo Nome é obrigatório."

        if dados['cpf'] and len(dados['cpf']) not in [11, 14]:
            return False, "CPF deve ter 11 dígitos ou CNPJ deve ter 14 dígitos."

        if dados['email'] and '@' not in dados['email']:
            return False, "Email deve ter um formato válido."

        return True, "Dados válidos."
