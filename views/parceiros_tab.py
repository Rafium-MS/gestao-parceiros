"""Tab responsável pelo CRUD de parceiros e vinculação com lojas."""

from __future__ import annotations

import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk

from models.repositories import (
    LojasRepository,
    ParceiroLojaRepository,
    ParceirosRepository,
)


class ParceirosTab:
    def __init__(
        self,
        notebook: ttk.Notebook,
        parceiros_repo: ParceirosRepository,
        lojas_repo: LojasRepository,
        vinculo_repo: ParceiroLojaRepository,
        on_change: callable | None = None,
    ) -> None:
        self._repo = parceiros_repo
        self._lojas_repo = lojas_repo
        self._vinculo_repo = vinculo_repo
        self._on_change = on_change

        self.frame = tk.Frame(notebook, bg="white")
        notebook.add(self.frame, text="🚚 Parceiros")

        self._build_ui()
        self.update_parceiros_combo()
        self.refresh()

    def _build_ui(self) -> None:
        parceiro_notebook = ttk.Notebook(self.frame)
        parceiro_notebook.pack(fill="both", expand=True, padx=5, pady=5)

        cadastro_tab = tk.Frame(parceiro_notebook, bg="white")
        parceiro_notebook.add(cadastro_tab, text="Cadastro de Parceiro")

        canvas = tk.Canvas(cadastro_tab, bg="white")
        scrollbar = ttk.Scrollbar(cadastro_tab, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="white")

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        cadastro_frame = tk.LabelFrame(
            scrollable_frame,
            text="Dados do Parceiro",
            font=("Arial", 11, "bold"),
            bg="white",
        )
        cadastro_frame.pack(fill="both", expand=True, padx=20, pady=10)
        for col in range(4):
            cadastro_frame.grid_columnconfigure(col, weight=1, uniform="cadastro")

        tk.Label(cadastro_frame, text="Nome do Parceiro:", bg="white").grid(
            row=0, column=0, padx=10, pady=5, sticky="w"
        )
        self.entry_nome = tk.Entry(cadastro_frame)
        self.entry_nome.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        tk.Label(cadastro_frame, text="Distribuidora:", bg="white").grid(
            row=0, column=2, padx=10, pady=5, sticky="w"
        )
        self.entry_distrib = tk.Entry(cadastro_frame)
        self.entry_distrib.grid(row=0, column=3, padx=10, pady=5, sticky="ew")

        tk.Label(cadastro_frame, text="Cidade:", bg="white").grid(
            row=1, column=0, padx=10, pady=5, sticky="w"
        )
        self.entry_cidade = tk.Entry(cadastro_frame)
        self.entry_cidade.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        tk.Label(cadastro_frame, text="Estado:", bg="white").grid(
            row=1, column=2, padx=10, pady=5, sticky="w"
        )
        self.entry_estado = tk.Entry(cadastro_frame)
        self.entry_estado.grid(row=1, column=3, padx=10, pady=5, sticky="ew")

        tk.Label(cadastro_frame, text="CNPJ:", bg="white").grid(
            row=2, column=0, padx=10, pady=5, sticky="w"
        )
        self.entry_cnpj = tk.Entry(cadastro_frame)
        self.entry_cnpj.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        tk.Label(cadastro_frame, text="Telefone:", bg="white").grid(
            row=2, column=2, padx=10, pady=5, sticky="w"
        )
        self.entry_telefone = tk.Entry(cadastro_frame)
        self.entry_telefone.grid(row=2, column=3, padx=10, pady=5, sticky="ew")

        tk.Label(cadastro_frame, text="Email:", bg="white").grid(
            row=3, column=0, padx=10, pady=5, sticky="w"
        )
        self.entry_email = tk.Entry(cadastro_frame)
        self.entry_email.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

        tk.Label(cadastro_frame, text="Dia do Pagamento:", bg="white").grid(
            row=3, column=2, padx=10, pady=5, sticky="w"
        )
        self.entry_dia_pagamento = tk.Entry(cadastro_frame)
        self.entry_dia_pagamento.grid(row=3, column=3, padx=10, pady=5, sticky="ew")

        tk.Label(cadastro_frame, text="Banco:", bg="white").grid(
            row=4, column=0, padx=10, pady=5, sticky="w"
        )
        self.entry_banco = tk.Entry(cadastro_frame)
        self.entry_banco.grid(row=4, column=1, padx=10, pady=5, sticky="ew")

        tk.Label(cadastro_frame, text="Agência:", bg="white").grid(
            row=4, column=2, padx=10, pady=5, sticky="w"
        )
        self.entry_agencia = tk.Entry(cadastro_frame)
        self.entry_agencia.grid(row=4, column=3, padx=10, pady=5, sticky="ew")

        tk.Label(cadastro_frame, text="Conta:", bg="white").grid(
            row=5, column=0, padx=10, pady=5, sticky="w"
        )
        self.entry_conta = tk.Entry(cadastro_frame)
        self.entry_conta.grid(row=5, column=1, padx=10, pady=5, sticky="ew")

        tk.Label(cadastro_frame, text="Chave PIX:", bg="white").grid(
            row=5, column=2, padx=10, pady=5, sticky="w"
        )
        self.entry_pix = tk.Entry(cadastro_frame)
        self.entry_pix.grid(row=5, column=3, padx=10, pady=5, sticky="ew")

        valores_frame = tk.LabelFrame(
            scrollable_frame,
            text="Valores do Parceiro (Pagamento)",
            font=("Arial", 11, "bold"),
            bg="white",
        )
        valores_frame.pack(fill="both", expand=True, padx=20, pady=10)
        for col in range(4):
            valores_frame.grid_columnconfigure(col, weight=1, uniform="valores")

        tk.Label(valores_frame, text="Valor 20L (R$):", bg="white").grid(
            row=0, column=0, padx=10, pady=5, sticky="w"
        )
        self.entry_valor_20l = tk.Entry(valores_frame)
        self.entry_valor_20l.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        tk.Label(valores_frame, text="Valor 10L (R$):", bg="white").grid(
            row=0, column=2, padx=10, pady=5, sticky="w"
        )
        self.entry_valor_10l = tk.Entry(valores_frame)
        self.entry_valor_10l.grid(row=0, column=3, padx=10, pady=5, sticky="ew")

        tk.Label(valores_frame, text="Valor Cx Copo (R$):", bg="white").grid(
            row=1, column=0, padx=10, pady=5, sticky="w"
        )
        self.entry_valor_cx_copo = tk.Entry(valores_frame)
        self.entry_valor_cx_copo.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        tk.Label(valores_frame, text="Valor 1500ml (R$):", bg="white").grid(
            row=1, column=2, padx=10, pady=5, sticky="w"
        )
        self.entry_valor_1500ml = tk.Entry(valores_frame)
        self.entry_valor_1500ml.grid(row=1, column=3, padx=10, pady=5, sticky="ew")

        btn_frame = tk.Frame(scrollable_frame, bg="white")
        btn_frame.pack(pady=10)

        tk.Button(
            btn_frame,
            text="Salvar Parceiro",
            bg="#2ecc71",
            fg="white",
            command=self.salvar,
            padx=20,
            pady=5,
        ).pack(side="left", padx=5)
        tk.Button(
            btn_frame,
            text="Limpar",
            bg="#95a5a6",
            fg="white",
            command=self.limpar,
            padx=20,
            pady=5,
        ).pack(side="left", padx=5)

        list_frame = tk.LabelFrame(
            scrollable_frame,
            text="Parceiros Cadastrados",
            font=("Arial", 11, "bold"),
            bg="white",
        )
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)

        columns = ("ID", "Nome", "Cidade", "Estado", "CNPJ", "Telefone")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=8)
        for column in columns:
            self.tree.heading(column, text=column)

        scrollbar_tree = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar_tree.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar_tree.pack(side="right", fill="y")

        list_frame.bind("<Configure>", lambda event: self._auto_size_parceiros_tree())

        action_frame = tk.Frame(scrollable_frame, bg="white")
        action_frame.pack(pady=10)

        tk.Button(
            action_frame,
            text="Editar",
            bg="#3498db",
            fg="white",
            command=self.editar,
            padx=15,
            pady=5,
        ).pack(side="left", padx=5)
        tk.Button(
            action_frame,
            text="Excluir",
            bg="#e74c3c",
            fg="white",
            command=self.excluir,
            padx=15,
            pady=5,
        ).pack(side="left", padx=5)
        tk.Button(
            action_frame,
            text="Atualizar Lista",
            bg="#95a5a6",
            fg="white",
            command=self.refresh,
            padx=15,
            pady=5,
        ).pack(side="left", padx=5)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self._build_vinculo_tab(parceiro_notebook)
        self._auto_size_parceiros_tree()

    def _build_vinculo_tab(self, notebook: ttk.Notebook) -> None:
        lojas_tab = tk.Frame(notebook, bg="white")
        notebook.add(lojas_tab, text="Lojas do Parceiro")

        sel_frame = tk.LabelFrame(
            lojas_tab,
            text="Selecione o Parceiro",
            font=("Arial", 11, "bold"),
            bg="white",
        )
        sel_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(sel_frame, text="Parceiro:", bg="white").pack(side="left", padx=10, pady=10)
        self.combo_vincular_parceiro = ttk.Combobox(sel_frame, width=50, state="readonly")
        self.combo_vincular_parceiro.pack(side="left", fill="x", expand=True, padx=10, pady=10)
        self.combo_vincular_parceiro.bind("<<ComboboxSelected>>", self.carregar_lojas_vinculacao)

        main_frame = tk.Frame(lojas_tab, bg="white")
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        self._lojas_layout = "horizontal"

        disponiveis_frame = tk.LabelFrame(
            main_frame,
            text="Lojas Disponíveis",
            font=("Arial", 10, "bold"),
            bg="white",
        )
        disponiveis_frame.pack(side="left", fill="both", expand=True, padx=5)

        self.tree_lojas_disponiveis = ttk.Treeview(
            disponiveis_frame,
            columns=("ID", "Nome", "Cidade", "Estado"),
            show="headings",
            height=15,
        )
        for column in ("ID", "Nome", "Cidade", "Estado"):
            self.tree_lojas_disponiveis.heading(column, text=column)
        scrollbar1 = ttk.Scrollbar(disponiveis_frame, orient="vertical", command=self.tree_lojas_disponiveis.yview)
        self.tree_lojas_disponiveis.configure(yscrollcommand=scrollbar1.set)
        self.tree_lojas_disponiveis.pack(side="left", fill="both", expand=True)
        scrollbar1.pack(side="right", fill="y")

        disponiveis_frame.bind("<Configure>", lambda event: self._auto_size_lojas_tree(self.tree_lojas_disponiveis))

        btn_frame = tk.Frame(main_frame, bg="white")
        btn_frame.pack(side="left", padx=10)

        tk.Button(
            btn_frame,
            text="➡️\nAdicionar",
            bg="#2ecc71",
            fg="white",
            command=self.vincular_loja,
            padx=10,
            pady=20,
        ).pack(pady=10)
        tk.Button(
            btn_frame,
            text="⬅️\nRemover",
            bg="#e74c3c",
            fg="white",
            command=self.desvincular_loja,
            padx=10,
            pady=20,
        ).pack(pady=10)

        vinculadas_frame = tk.LabelFrame(
            main_frame,
            text="Lojas Vinculadas",
            font=("Arial", 10, "bold"),
            bg="white",
        )
        vinculadas_frame.pack(side="left", fill="both", expand=True, padx=5)

        self.tree_lojas_vinculadas = ttk.Treeview(
            vinculadas_frame,
            columns=("ID", "Nome", "Cidade", "Estado"),
            show="headings",
            height=15,
        )
        for column in ("ID", "Nome", "Cidade", "Estado"):
            self.tree_lojas_vinculadas.heading(column, text=column)
        scrollbar2 = ttk.Scrollbar(vinculadas_frame, orient="vertical", command=self.tree_lojas_vinculadas.yview)
        self.tree_lojas_vinculadas.configure(yscrollcommand=scrollbar2.set)
        self.tree_lojas_vinculadas.pack(side="left", fill="both", expand=True)
        scrollbar2.pack(side="right", fill="y")

        vinculadas_frame.bind("<Configure>", lambda event: self._auto_size_lojas_tree(self.tree_lojas_vinculadas))
        main_frame.bind(
            "<Configure>",
            lambda event, df=disponiveis_frame, bf=btn_frame, vf=vinculadas_frame: self._adjust_lojas_layout(event, df, bf, vf),
        )
        self._auto_size_lojas_tree(self.tree_lojas_disponiveis)
        self._auto_size_lojas_tree(self.tree_lojas_vinculadas)

    def set_on_change(self, callback: callable | None) -> None:
        self._on_change = callback

    def update_parceiros_combo(self) -> None:
        values = list(self._repo.combo_values())
        self.combo_vincular_parceiro["values"] = values

    def _auto_size_parceiros_tree(self) -> None:
        total_width = self.tree.winfo_width()
        if total_width <= 0:
            return

        def set_width(column: str, fraction: float, minimum: int) -> None:
            self.tree.column(column, width=max(int(total_width * fraction), minimum))

        set_width("ID", 0.08, 70)
        set_width("Nome", 0.32, 160)
        set_width("Cidade", 0.18, 120)
        set_width("Estado", 0.1, 80)
        set_width("CNPJ", 0.18, 140)
        set_width("Telefone", 0.14, 120)

    def _auto_size_lojas_tree(self, tree: ttk.Treeview) -> None:
        total_width = tree.winfo_width()
        if total_width <= 0:
            return

        def set_width(column: str, fraction: float, minimum: int) -> None:
            tree.column(column, width=max(int(total_width * fraction), minimum))

        set_width("ID", 0.12, 70)
        set_width("Nome", 0.46, 180)
        set_width("Cidade", 0.27, 120)
        set_width("Estado", 0.15, 70)

    def _adjust_lojas_layout(
        self,
        event: tk.Event,
        disponiveis_frame: tk.Widget,
        btn_frame: tk.Widget,
        vinculadas_frame: tk.Widget,
    ) -> None:
        width = event.width
        layout = "vertical" if width < 900 else "horizontal"
        if layout == self._lojas_layout:
            return

        if layout == "horizontal":
            disponiveis_frame.pack_configure(side="left", fill="both", expand=True, padx=5, pady=0)
            btn_frame.pack_configure(side="left", padx=10, pady=0)
            vinculadas_frame.pack_configure(side="left", fill="both", expand=True, padx=5, pady=0)
        else:
            disponiveis_frame.pack_configure(side="top", fill="both", expand=True, padx=5, pady=5)
            btn_frame.pack_configure(side="top", pady=10)
            vinculadas_frame.pack_configure(side="top", fill="both", expand=True, padx=5, pady=5)

        self._lojas_layout = layout

    def _parse_float(self, value: str) -> float | None:
        value = value.strip()
        if not value:
            return None
        return float(value.replace(",", "."))

    def salvar(self) -> None:
        nome = self.entry_nome.get().strip()
        if not nome:
            messagebox.showwarning("Atenção", "Informe o nome do parceiro!")
            return

        try:
            dia_pagamento = int(self.entry_dia_pagamento.get()) if self.entry_dia_pagamento.get().strip() else None
        except ValueError:
            messagebox.showerror("Erro", "Dia de pagamento inválido!")
            return

        try:
            self._repo.add(
                nome,
                self.entry_distrib.get().strip(),
                self.entry_cidade.get().strip(),
                self.entry_estado.get().strip(),
                self.entry_cnpj.get().strip(),
                self.entry_telefone.get().strip(),
                self.entry_email.get().strip(),
                dia_pagamento,
                self.entry_banco.get().strip(),
                self.entry_agencia.get().strip(),
                self.entry_conta.get().strip(),
                self.entry_pix.get().strip(),
                self._parse_float(self.entry_valor_20l.get()),
                self._parse_float(self.entry_valor_10l.get()),
                self._parse_float(self.entry_valor_cx_copo.get()),
                self._parse_float(self.entry_valor_1500ml.get()),
            )
        except ValueError:
            messagebox.showerror("Erro", "Valores numéricos inválidos!")
            return

        messagebox.showinfo("Sucesso", "Parceiro cadastrado com sucesso!")
        self.limpar()
        self.refresh()
        self.update_parceiros_combo()
        if self._on_change:
            self._on_change()

    def limpar(self) -> None:
        for entry in (
            self.entry_nome,
            self.entry_distrib,
            self.entry_cidade,
            self.entry_estado,
            self.entry_cnpj,
            self.entry_telefone,
            self.entry_email,
            self.entry_dia_pagamento,
            self.entry_banco,
            self.entry_agencia,
            self.entry_conta,
            self.entry_pix,
            self.entry_valor_20l,
            self.entry_valor_10l,
            self.entry_valor_cx_copo,
            self.entry_valor_1500ml,
        ):
            entry.delete(0, tk.END)

    def refresh(self) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)

        for row in self._repo.list_all():
            self.tree.insert("", "end", values=row)

    def editar(self) -> None:
        messagebox.showinfo("Info", "Função de edição será implementada")

    def excluir(self) -> None:
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Atenção", "Selecione um parceiro!")
            return

        if not messagebox.askyesno("Confirmar", "Deseja realmente excluir este parceiro?"):
            return

        item = self.tree.item(selected[0])
        parceiro_id = item["values"][0]

        self._repo.delete(parceiro_id)
        messagebox.showinfo("Sucesso", "Parceiro excluído!")
        self.refresh()
        self.update_parceiros_combo()
        if self._on_change:
            self._on_change()

    def carregar_lojas_vinculacao(self, event: tk.Event | None = None) -> None:
        parceiro = self.combo_vincular_parceiro.get()
        if not parceiro:
            return

        parceiro_id = int(parceiro.split(" - ")[0])

        for tree in (self.tree_lojas_disponiveis, self.tree_lojas_vinculadas):
            for item in tree.get_children():
                tree.delete(item)

        for row in self._vinculo_repo.list_vinculadas(parceiro_id):
            self.tree_lojas_vinculadas.insert("", "end", values=row)

        for row in self._vinculo_repo.list_disponiveis(parceiro_id):
            self.tree_lojas_disponiveis.insert("", "end", values=row)

    def vincular_loja(self) -> None:
        parceiro = self.combo_vincular_parceiro.get()
        if not parceiro:
            messagebox.showwarning("Atenção", "Selecione um parceiro!")
            return

        selected = self.tree_lojas_disponiveis.selection()
        if not selected:
            messagebox.showwarning("Atenção", "Selecione uma loja!")
            return

        parceiro_id = int(parceiro.split(" - ")[0])
        loja_id = self.tree_lojas_disponiveis.item(selected[0])["values"][0]

        try:
            self._vinculo_repo.vincular(parceiro_id, loja_id)
        except sqlite3.IntegrityError:
            messagebox.showwarning("Atenção", "Loja já vinculada!")
            return

        self.carregar_lojas_vinculacao()
        messagebox.showinfo("Sucesso", "Loja vinculada!")
        if self._on_change:
            self._on_change()

    def desvincular_loja(self) -> None:
        parceiro = self.combo_vincular_parceiro.get()
        if not parceiro:
            return

        selected = self.tree_lojas_vinculadas.selection()
        if not selected:
            messagebox.showwarning("Atenção", "Selecione uma loja!")
            return

        parceiro_id = int(parceiro.split(" - ")[0])
        loja_id = self.tree_lojas_vinculadas.item(selected[0])["values"][0]

        self._vinculo_repo.desvincular(parceiro_id, loja_id)
        self.carregar_lojas_vinculacao()
        messagebox.showinfo("Sucesso", "Loja desvinculada!")
        if self._on_change:
            self._on_change()

