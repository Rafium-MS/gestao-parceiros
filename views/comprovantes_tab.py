"""Tab para cadastro e gestão de comprovantes de entrega."""

from __future__ import annotations

from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from models.repositories import ComprovantesRepository, ParceiroLojaRepository, ParceirosRepository


class ComprovantesTab:
    def __init__(
        self,
        notebook: ttk.Notebook,
        comprovantes_repo: ComprovantesRepository,
        parceiros_repo: ParceirosRepository,
        vinculo_repo: ParceiroLojaRepository,
        on_change: callable | None = None,
    ) -> None:
        self._repo = comprovantes_repo
        self._parceiros_repo = parceiros_repo
        self._vinculo_repo = vinculo_repo
        self._on_change = on_change

        self.frame = tk.Frame(notebook, bg="white")
        notebook.add(self.frame, text="📋 Comprovantes")

        self._build_ui()
        self.refresh_parceiros()
        self.refresh_list()

    def _build_ui(self) -> None:
        cadastro_frame = tk.LabelFrame(
            self.frame,
            text="Registrar Comprovante de Entrega",
            font=("Arial", 11, "bold"),
            bg="white",
        )
        cadastro_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(cadastro_frame, text="Parceiro:", bg="white").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.combo_parceiro = ttk.Combobox(cadastro_frame, width=35, state="readonly")
        self.combo_parceiro.grid(row=0, column=1, padx=10, pady=5)
        self.combo_parceiro.bind("<<ComboboxSelected>>", self.atualizar_lojas)

        tk.Label(cadastro_frame, text="Loja:", bg="white").grid(row=0, column=2, padx=10, pady=5, sticky="w")
        self.combo_loja = ttk.Combobox(cadastro_frame, width=35, state="readonly")
        self.combo_loja.grid(row=0, column=3, padx=10, pady=5)

        tk.Label(cadastro_frame, text="Data da Entrega:", bg="white").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.entry_data = tk.Entry(cadastro_frame, width=38)
        self.entry_data.grid(row=1, column=1, padx=10, pady=5)
        self.entry_data.insert(0, datetime.now().strftime("%d/%m/%Y"))

        tk.Label(cadastro_frame, text="Assinatura:", bg="white").grid(row=1, column=2, padx=10, pady=5, sticky="w")
        self.entry_assinatura = tk.Entry(cadastro_frame, width=38)
        self.entry_assinatura.grid(row=1, column=3, padx=10, pady=5)

        produtos_frame = tk.LabelFrame(cadastro_frame, text="Produtos Entregues", bg="white")
        produtos_frame.grid(row=2, column=0, columnspan=4, padx=10, pady=10, sticky="ew")

        tk.Label(produtos_frame, text="Qtd 20L:", bg="white").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.entry_qtd_20l = tk.Entry(produtos_frame, width=15)
        self.entry_qtd_20l.grid(row=0, column=1, padx=10, pady=5)
        self.entry_qtd_20l.insert(0, "0")

        tk.Label(produtos_frame, text="Qtd 10L:", bg="white").grid(row=0, column=2, padx=10, pady=5, sticky="w")
        self.entry_qtd_10l = tk.Entry(produtos_frame, width=15)
        self.entry_qtd_10l.grid(row=0, column=3, padx=10, pady=5)
        self.entry_qtd_10l.insert(0, "0")

        tk.Label(produtos_frame, text="Qtd Cx Copo:", bg="white").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.entry_qtd_cx_copo = tk.Entry(produtos_frame, width=15)
        self.entry_qtd_cx_copo.grid(row=1, column=1, padx=10, pady=5)
        self.entry_qtd_cx_copo.insert(0, "0")

        tk.Label(produtos_frame, text="Qtd 1500ml:", bg="white").grid(row=1, column=2, padx=10, pady=5, sticky="w")
        self.entry_qtd_1500ml = tk.Entry(produtos_frame, width=15)
        self.entry_qtd_1500ml.grid(row=1, column=3, padx=10, pady=5)
        self.entry_qtd_1500ml.insert(0, "0")

        tk.Label(cadastro_frame, text="Arquivo (opcional):", bg="white").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.entry_arquivo = tk.Entry(cadastro_frame, width=50)
        self.entry_arquivo.grid(row=3, column=1, columnspan=2, padx=10, pady=5)
        tk.Button(cadastro_frame, text="Selecionar", command=self.selecionar_arquivo).grid(row=3, column=3, padx=10, pady=5)

        btn_frame = tk.Frame(cadastro_frame, bg="white")
        btn_frame.grid(row=4, column=0, columnspan=4, pady=10)

        tk.Button(
            btn_frame,
            text="Salvar Comprovante",
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
            self.frame,
            text="Comprovantes Registrados",
            font=("Arial", 11, "bold"),
            bg="white",
        )
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)

        columns = ("ID", "Data", "Parceiro", "Loja", "20L", "10L", "Cx Copo", "1500ml")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=12)
        for column in columns:
            self.tree.heading(column, text=column)

        self.tree.column("ID", width=50)
        self.tree.column("Data", width=100)
        self.tree.column("Parceiro", width=150)
        self.tree.column("Loja", width=150)
        self.tree.column("20L", width=80)
        self.tree.column("10L", width=80)
        self.tree.column("Cx Copo", width=80)
        self.tree.column("1500ml", width=80)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        action_frame = tk.Frame(self.frame, bg="white")
        action_frame.pack(pady=10)

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
            command=self.refresh_list,
            padx=15,
            pady=5,
        ).pack(side="left", padx=5)

    def set_on_change(self, callback: callable | None) -> None:
        self._on_change = callback

    def refresh_parceiros(self) -> None:
        values = list(self._parceiros_repo.combo_values())
        self.combo_parceiro["values"] = values
        self.combo_loja.set("")

    def atualizar_lojas(self, event: tk.Event | None = None) -> None:
        parceiro = self.combo_parceiro.get()
        if not parceiro:
            self.combo_loja["values"] = []
            return

        parceiro_id = int(parceiro.split(" - ")[0])
        self.combo_loja["values"] = list(self._vinculo_repo.lojas_para_parceiro(parceiro_id))
        self.combo_loja.set("")

    def selecionar_arquivo(self) -> None:
        filename = filedialog.askopenfilename(
            title="Selecionar Comprovante",
            filetypes=[("Imagens", "*.png *.jpg *.jpeg"), ("PDF", "*.pdf"), ("Todos", "*.*")],
        )
        if filename:
            self.entry_arquivo.delete(0, tk.END)
            self.entry_arquivo.insert(0, filename)

    def _parse_int(self, value: str) -> int:
        value = value.strip() or "0"
        return int(value)

    def salvar(self) -> None:
        parceiro = self.combo_parceiro.get()
        loja = self.combo_loja.get()

        if not parceiro or not loja:
            messagebox.showwarning("Atenção", "Selecione parceiro e loja!")
            return

        parceiro_id = int(parceiro.split(" - ")[0])
        loja_id = int(loja.split(" - ")[0])

        data = self.entry_data.get().strip()
        try:
            data_sql = datetime.strptime(data, "%d/%m/%Y").strftime("%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Erro", "Data inválida! Use o formato DD/MM/AAAA")
            return

        try:
            self._repo.add(
                parceiro_id,
                loja_id,
                data_sql,
                self._parse_int(self.entry_qtd_20l.get()),
                self._parse_int(self.entry_qtd_10l.get()),
                self._parse_int(self.entry_qtd_cx_copo.get()),
                self._parse_int(self.entry_qtd_1500ml.get()),
                self.entry_assinatura.get().strip(),
                self.entry_arquivo.get().strip(),
            )
        except ValueError:
            messagebox.showerror("Erro", "Quantidades inválidas!")
            return

        messagebox.showinfo("Sucesso", "Comprovante registrado!")
        self.limpar()
        self.refresh_list()
        if self._on_change:
            self._on_change()

    def limpar(self) -> None:
        self.combo_parceiro.set("")
        self.combo_loja.set("")
        self.entry_data.delete(0, tk.END)
        self.entry_data.insert(0, datetime.now().strftime("%d/%m/%Y"))
        self.entry_assinatura.delete(0, tk.END)
        for entry in (
            self.entry_qtd_20l,
            self.entry_qtd_10l,
            self.entry_qtd_cx_copo,
            self.entry_qtd_1500ml,
        ):
            entry.delete(0, tk.END)
            entry.insert(0, "0")
        self.entry_arquivo.delete(0, tk.END)

    def refresh_list(self) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)

        for row in self._repo.list_all():
            data_format = datetime.strptime(row[1], "%Y-%m-%d").strftime("%d/%m/%Y")
            values = (row[0], data_format, row[2], row[3], row[4], row[5], row[6], row[7])
            self.tree.insert("", "end", values=values)

    def excluir(self) -> None:
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Atenção", "Selecione um comprovante!")
            return

        if not messagebox.askyesno("Confirmar", "Deseja realmente excluir este comprovante?"):
            return

        item = self.tree.item(selected[0])
        comprovante_id = item["values"][0]

        self._repo.delete(comprovante_id)
        messagebox.showinfo("Sucesso", "Comprovante excluído!")
        self.refresh_list()
        if self._on_change:
            self._on_change()

