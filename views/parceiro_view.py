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
from utils.tooltip import ToolTip


class ParceiroView(ttk.Frame):
    """Interface gráfica para gerenciamento de parceiros."""

    def __init__(self, parent, db_manager):
        super().__init__(parent)
        self.parent = parent
        self.logger = logging.getLogger(__name__)
        self.controller = ParceiroController(db_manager)
        self.parceiro_atual_id = None

        self._criar_widgets()
        self._configurar_eventos()
        self._carregar_parceiros()

    def _criar_widgets(self):
        """Cria os widgets da interface."""
        # Frame Informações do Parceiro
        self.frame_info = ttk.LabelFrame(self, text="Informações do Parceiro")
        self.frame_info.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(self.frame_info, text="Nome:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.entrada_nome = ttk.Entry(self.frame_info, width=40)
        self.entrada_nome.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.frame_info, text="CPF/CNPJ:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.entrada_cpf = ttk.Entry(self.frame_info, width=20)
        self.entrada_cpf.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(self.frame_info, text="Telefone:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.entrada_telefone = ttk.Entry(self.frame_info, width=20)
        self.entrada_telefone.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self.frame_info, text="Email:").grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)
        self.entrada_email = ttk.Entry(self.frame_info, width=30)
        self.entrada_email.grid(row=1, column=3, padx=5, pady=5)

        ttk.Label(self.frame_info, text="Endereço:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.entrada_endereco = ttk.Entry(self.frame_info, width=60)
        self.entrada_endereco.grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky=tk.EW)

        ttk.Label(self.frame_info, text="Cidade:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.entrada_cidade = ttk.Entry(self.frame_info, width=30)
        self.entrada_cidade.grid(row=3, column=1, padx=5, pady=5)

        ttk.Label(self.frame_info, text="Estado:").grid(row=3, column=2, padx=5, pady=5, sticky=tk.W)
        self.entrada_estado = ttk.Entry(self.frame_info, width=5)
        self.entrada_estado.grid(row=3, column=3, padx=5, pady=5, sticky=tk.W)

        # Frame Informações Financeiras
        self.frame_financeiro = ttk.LabelFrame(self, text="Informações Financeiras")
        self.frame_financeiro.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(self.frame_financeiro, text="Banco:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.entrada_banco = ttk.Entry(self.frame_financeiro, width=20)
        self.entrada_banco.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.frame_financeiro, text="Agência:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.entrada_agencia = ttk.Entry(self.frame_financeiro, width=10)
        self.entrada_agencia.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)

        ttk.Label(self.frame_financeiro, text="Conta:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.entrada_conta = ttk.Entry(self.frame_financeiro, width=20)
        self.entrada_conta.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self.frame_financeiro, text="Tipo:").grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)
        self.combo_tipo = ttk.Combobox(self.frame_financeiro, values=["Corrente", "Poupança", "Pix"], width=10, state="readonly")
        self.combo_tipo.grid(row=1, column=3, padx=5, pady=5, sticky=tk.W)

        # Frame Produtos
        self.frame_produtos = ttk.LabelFrame(self, text="Produtos e Valores")
        self.frame_produtos.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        ttk.Label(self.frame_produtos, text="Produto:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.entrada_produto = ttk.Entry(self.frame_produtos, width=30)
        self.entrada_produto.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.frame_produtos, text="Valor Unidade:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.entrada_valor = ttk.Entry(self.frame_produtos, width=10)
        self.entrada_valor.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)

        self.btn_add_produto = ttk.Button(self.frame_produtos, text="+ Adicionar Produto",
                                          command=self._adicionar_produto)
        self.btn_add_produto.grid(row=0, column=4, padx=10, pady=5)

        self.tree_produtos = ttk.Treeview(self.frame_produtos, columns=("produto", "valor"), show="headings", height=5)
        self.tree_produtos.heading("produto", text="Produto")
        self.tree_produtos.heading("valor", text="Valor Unitário")
        self.tree_produtos.column("produto", width=300)
        self.tree_produtos.column("valor", width=100)
        self.tree_produtos.grid(row=1, column=0, columnspan=5, padx=5, pady=10, sticky="nsew")

        self.frame_produtos.rowconfigure(1, weight=1)
        self.frame_produtos.columnconfigure(1, weight=1)

        # Frame Botões
        self.frame_botoes = ttk.Frame(self)
        self.frame_botoes.pack(pady=10)

        self.btn_adicionar = ttk.Button(self.frame_botoes, text="Adicionar", command=self._adicionar_parceiro)
        self.btn_adicionar.pack(side=tk.LEFT, padx=5)
        ToolTip(self.btn_adicionar, "Adiciona um novo parceiro ao sistema")

        self.btn_editar = ttk.Button(self.frame_botoes, text="Salvar Edição", command=self._editar_parceiro,
                                     state=tk.DISABLED)
        self.btn_editar.pack(side=tk.LEFT, padx=5)
        ToolTip(self.btn_editar, "Salva alterações no parceiro selecionado")

        self.btn_excluir = ttk.Button(self.frame_botoes, text="Excluir", command=self._excluir_parceiro,
                                      state=tk.DISABLED)
        self.btn_excluir.pack(side=tk.LEFT, padx=5)
        ToolTip(self.btn_excluir, "Remove o parceiro selecionado")

        self.btn_limpar = ttk.Button(self.frame_botoes, text="Limpar", command=self._limpar_form)
        self.btn_limpar.pack(side=tk.LEFT, padx=5)
        ToolTip(self.btn_limpar, "Limpa o formulário")

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
        colunas = (
            "id",
            "nome",
            "cpf",
            "telefone",
            "email",
            "endereco",
            "cidade",
            "estado",
            "produto",
            "valor",
            "data_cadastro",
        )
        self.treeview = ttk.Treeview(self.frame_lista, columns=colunas, show="headings", selectmode="browse")

        # Definir cabeçalhos
        self.treeview.heading("id", text="ID")
        self.treeview.heading("nome", text="Nome")
        self.treeview.heading("cpf", text="CPF")
        self.treeview.heading("telefone", text="Telefone")
        self.treeview.heading("email", text="Email")
        self.treeview.heading("endereco", text="Endereço")
        self.treeview.heading("cidade", text="Cidade")
        self.treeview.heading("estado", text="Estado")
        self.treeview.heading("produto", text="Produto")
        self.treeview.heading("valor", text="Valor Unid.")
        self.treeview.heading("data_cadastro", text="Data de Cadastro")

        # Definir larguras das colunas
        self.treeview.column("id", width=50, minwidth=50)
        self.treeview.column("nome", width=200, minwidth=150)
        self.treeview.column("cpf", width=120, minwidth=100)
        self.treeview.column("telefone", width=120, minwidth=100)
        self.treeview.column("email", width=180, minwidth=120)
        self.treeview.column("endereco", width=200, minwidth=150)
        self.treeview.column("cidade", width=120, minwidth=100)
        self.treeview.column("estado", width=60, minwidth=50)
        self.treeview.column("produto", width=120, minwidth=100)
        self.treeview.column("valor", width=80, minwidth=60)
        self.treeview.column("data_cadastro", width=120, minwidth=100)

        # Scrollbar
        scrollbar = ttk.Scrollbar(self.frame_lista, orient=tk.VERTICAL, command=self.treeview.yview)
        self.treeview.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.treeview.pack(fill=tk.BOTH, expand=True)

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
            self.entrada_cidade.insert(0, valores[6] if valores[6] else "")
            self.entrada_estado.insert(0, valores[7] if valores[7] else "")
            self.entrada_produto.insert(0, valores[8] if valores[8] else "")
            self.entrada_valor.insert(0, valores[9] if valores[9] else "")

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
            'endereco': self.entrada_endereco.get().strip(),
            'cidade': self.entrada_cidade.get().strip(),
            'estado': self.entrada_estado.get().strip(),
            'banco': self.entrada_banco.get().strip(),
            'agencia': self.entrada_agencia.get().strip(),
            'conta': self.entrada_conta.get().strip(),
            'tipo': self.combo_tipo.get().strip(),
            'produto': self.entrada_produto.get().strip(),
            'valor_unidade': self.entrada_valor.get().strip(),
        }

        ToolTip(self.entrada_nome, "Digite o nome completo do parceiro")
        ToolTip(self.entrada_cpf, "CPF no formato 000.000.000-00 (opcional)")

    def _limpar_form(self):
        """Limpa o formulário e reseta o estado dos botões."""
        # Limpar campos
        self.entrada_nome.delete(0, tk.END)
        self.entrada_cpf.delete(0, tk.END)
        self.entrada_telefone.delete(0, tk.END)
        self.entrada_email.delete(0, tk.END)
        self.entrada_endereco.delete(0, tk.END)
        self.entrada_cidade.delete(0, tk.END)
        self.entrada_estado.delete(0, tk.END)
        self.entrada_banco.delete(0, tk.END)
        self.entrada_agencia.delete(0, tk.END)
        self.entrada_conta.delete(0, tk.END)
        self.combo_tipo.set("")
        self.entrada_produto.delete(0, tk.END)
        self.entrada_valor.delete(0, tk.END)

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
            cidade = dados.get("cidade")
            if cidade:
                lojas = self.loja_controller.obter_lojas_por_cidade(cidade)
                if lojas:
                    nomes = "\n".join(l["nome"] for l in lojas)
                    messagebox.showinfo(
                        "Lojas Sugeridas",
                        f"Lojas em {cidade} disponíveis para associação:\n{nomes}",
                    )
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
            cidade = dados.get("cidade")
            if cidade:
                lojas = self.loja_controller.obter_lojas_por_cidade(cidade)
                if lojas:
                    nomes = "\n".join(l["nome"] for l in lojas)
                    messagebox.showinfo(
                        "Lojas Sugeridas",
                        f"Lojas em {cidade} disponíveis para associação:\n{nomes}",
                    )
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
                parceiro[7],  # cidade
                parceiro[8],  # estado
                parceiro[13],  # produto
                parceiro[14],  # valor_unidade
                parceiro[6],  # data_cadastro
            )

            tag = 'evenrow' if index % 2 == 0 else 'oddrow'
            self.treeview.insert("", "end", values=valores, tags=(tag,))

    def _adicionar_produto(self):
        nome = self.entrada_produto.get().strip()
        valor = self.entrada_valor.get().strip()

        if not nome or not valor:
            messagebox.showwarning("Campos obrigatórios", "Informe o produto e o valor unitário.")
            return

        try:
            valor_float = float(valor)
        except ValueError:
            messagebox.showerror("Valor inválido", "O valor deve ser numérico.")
            return

        self.tree_produtos.insert("", "end", values=(nome, f"R$ {valor_float:.2f}"))
        self.produtos_adicionados.append({"produto": nome, "valor": valor_float})

        self.entrada_produto.delete(0, tk.END)
        self.entrada_valor.delete(0, tk.END)

    def focus_nome(self):
        """Coloca o foco no campo de nome."""
        self.entrada_nome.focus_set()