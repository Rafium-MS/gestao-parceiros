"""Tab responsável pelos relatórios do sistema."""

from __future__ import annotations

from datetime import datetime
import tkinter as tk
from tkinter import messagebox, ttk

from models.repositories import ComprovantesRepository, MarcasRepository, ParceirosRepository


class RelatoriosTab:
    def __init__(
        self,
        notebook: ttk.Notebook,
        comprovantes_repo: ComprovantesRepository,
        marcas_repo: MarcasRepository,
        parceiros_repo: ParceirosRepository,
    ) -> None:
        self._repo = comprovantes_repo
        self._marcas_repo = marcas_repo
        self._parceiros_repo = parceiros_repo

        self.frame = tk.Frame(notebook, bg="white")
        notebook.add(self.frame, text="📊 Relatórios")

        self._build_ui()
        self.update_marcas()
        self.update_parceiros()

    def _build_ui(self) -> None:
        rel_notebook = ttk.Notebook(self.frame)
        rel_notebook.pack(fill="both", expand=True, padx=5, pady=5)

        marca_tab = tk.Frame(rel_notebook, bg="white")
        rel_notebook.add(marca_tab, text="Relatório por Marca")

        filtro_frame = tk.LabelFrame(marca_tab, text="Filtros", font=("Arial", 11, "bold"), bg="white")
        filtro_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(filtro_frame, text="Marca:", bg="white").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.combo_marca = ttk.Combobox(filtro_frame, width=30, state="readonly")
        self.combo_marca.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(filtro_frame, text="Data Início:", bg="white").grid(row=0, column=2, padx=10, pady=5, sticky="w")
        self.entry_marca_inicio = tk.Entry(filtro_frame, width=15)
        self.entry_marca_inicio.grid(row=0, column=3, padx=10, pady=5)

        tk.Label(filtro_frame, text="Data Fim:", bg="white").grid(row=0, column=4, padx=10, pady=5, sticky="w")
        self.entry_marca_fim = tk.Entry(filtro_frame, width=15)
        self.entry_marca_fim.grid(row=0, column=5, padx=10, pady=5)

        tk.Button(
            filtro_frame,
            text="Gerar Relatório",
            bg="#3498db",
            fg="white",
            command=self.gerar_relatorio_marca,
            padx=20,
            pady=5,
        ).grid(row=0, column=6, padx=10, pady=5)

        resultado_frame = tk.LabelFrame(marca_tab, text="Resultado", font=("Arial", 11, "bold"), bg="white")
        resultado_frame.pack(fill="both", expand=True, padx=20, pady=10)

        columns = ("Loja", "Local", "Município", "20L", "10L", "Cx Copo", "1500ml", "Total (R$)")
        self.tree_marca = ttk.Treeview(resultado_frame, columns=columns, show="headings", height=15)
        for column in columns:
            self.tree_marca.heading(column, text=column)

        self.tree_marca.column("Loja", width=150)
        self.tree_marca.column("Local", width=150)
        self.tree_marca.column("Município", width=120)
        self.tree_marca.column("20L", width=60)
        self.tree_marca.column("10L", width=60)
        self.tree_marca.column("Cx Copo", width=80)
        self.tree_marca.column("1500ml", width=80)
        self.tree_marca.column("Total (R$)", width=100)

        scrollbar = ttk.Scrollbar(resultado_frame, orient="vertical", command=self.tree_marca.yview)
        self.tree_marca.configure(yscrollcommand=scrollbar.set)
        self.tree_marca.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        total_frame = tk.Frame(marca_tab, bg="white")
        total_frame.pack(fill="x", padx=20, pady=10)

        self.lbl_total_marca = tk.Label(total_frame, text="Total Geral: R$ 0,00", font=("Arial", 12, "bold"), bg="white")
        self.lbl_total_marca.pack(side="right", padx=10)

        tk.Button(
            total_frame,
            text="Exportar para Excel",
            bg="#2ecc71",
            fg="white",
            command=lambda: self.exportar_relatorio("marca"),
            padx=15,
            pady=5,
        ).pack(side="left", padx=5)

        parceiro_tab = tk.Frame(rel_notebook, bg="white")
        rel_notebook.add(parceiro_tab, text="Relatório por Parceiro")

        filtro_frame2 = tk.LabelFrame(parceiro_tab, text="Filtros", font=("Arial", 11, "bold"), bg="white")
        filtro_frame2.pack(fill="x", padx=20, pady=10)

        tk.Label(filtro_frame2, text="Parceiro:", bg="white").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.combo_parceiro = ttk.Combobox(filtro_frame2, width=30, state="readonly")
        self.combo_parceiro.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(filtro_frame2, text="Data Início:", bg="white").grid(row=0, column=2, padx=10, pady=5, sticky="w")
        self.entry_parceiro_inicio = tk.Entry(filtro_frame2, width=15)
        self.entry_parceiro_inicio.grid(row=0, column=3, padx=10, pady=5)

        tk.Label(filtro_frame2, text="Data Fim:", bg="white").grid(row=0, column=4, padx=10, pady=5, sticky="w")
        self.entry_parceiro_fim = tk.Entry(filtro_frame2, width=15)
        self.entry_parceiro_fim.grid(row=0, column=5, padx=10, pady=5)

        tk.Button(
            filtro_frame2,
            text="Gerar Relatório",
            bg="#3498db",
            fg="white",
            command=self.gerar_relatorio_parceiro,
            padx=20,
            pady=5,
        ).grid(row=0, column=6, padx=10, pady=5)

        resultado_frame2 = tk.LabelFrame(parceiro_tab, text="Resultado", font=("Arial", 11, "bold"), bg="white")
        resultado_frame2.pack(fill="both", expand=True, padx=20, pady=10)

        columns2 = ("Loja", "Data", "20L", "10L", "Cx Copo", "1500ml", "Total (R$)")
        self.tree_parceiro = ttk.Treeview(resultado_frame2, columns=columns2, show="headings", height=15)
        for column in columns2:
            self.tree_parceiro.heading(column, text=column)

        self.tree_parceiro.column("Loja", width=200)
        self.tree_parceiro.column("Data", width=100)
        self.tree_parceiro.column("20L", width=80)
        self.tree_parceiro.column("10L", width=80)
        self.tree_parceiro.column("Cx Copo", width=100)
        self.tree_parceiro.column("1500ml", width=100)
        self.tree_parceiro.column("Total (R$)", width=120)

        scrollbar2 = ttk.Scrollbar(resultado_frame2, orient="vertical", command=self.tree_parceiro.yview)
        self.tree_parceiro.configure(yscrollcommand=scrollbar2.set)
        self.tree_parceiro.pack(side="left", fill="both", expand=True)
        scrollbar2.pack(side="right", fill="y")

        total_frame2 = tk.Frame(parceiro_tab, bg="white")
        total_frame2.pack(fill="x", padx=20, pady=10)

        self.lbl_total_parceiro = tk.Label(total_frame2, text="Total a Receber: R$ 0,00", font=("Arial", 12, "bold"), bg="white")
        self.lbl_total_parceiro.pack(side="right", padx=10)

        tk.Button(
            total_frame2,
            text="Exportar para Excel",
            bg="#2ecc71",
            fg="white",
            command=lambda: self.exportar_relatorio("parceiro"),
            padx=15,
            pady=5,
        ).pack(side="left", padx=5)

    def update_marcas(self) -> None:
        self.combo_marca["values"] = list(self._marcas_repo.combo_values())

    def update_parceiros(self) -> None:
        self.combo_parceiro["values"] = list(self._parceiros_repo.combo_values())

    def _parse_date(self, value: str) -> str | None:
        value = value.strip()
        if not value:
            return None
        try:
            return datetime.strptime(value, "%d/%m/%Y").strftime("%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Atenção", f"Data inválida: {value}")
            return None

    def gerar_relatorio_marca(self) -> None:
        marca = self.combo_marca.get()
        if not marca:
            messagebox.showwarning("Atenção", "Selecione uma marca!")
            return

        marca_id = int(marca.split(" - ")[0])
        data_inicio = self._parse_date(self.entry_marca_inicio.get())
        data_fim = self._parse_date(self.entry_marca_fim.get())

        for item in self.tree_marca.get_children():
            self.tree_marca.delete(item)

        total_geral = 0.0
        for row in self._repo.relatorio_por_marca(marca_id, data_inicio, data_fim):
            nome, local, municipio, qtd_20l, qtd_10l, qtd_cx_copo, qtd_1500ml, val_20l, val_10l, val_copo, val_1500 = row
            total = (qtd_20l or 0) * (val_20l or 0) + (qtd_10l or 0) * (val_10l or 0) + (qtd_cx_copo or 0) * (val_copo or 0) + (qtd_1500ml or 0) * (val_1500 or 0)
            total_geral += total
            valores = (nome, local, municipio, qtd_20l or 0, qtd_10l or 0, qtd_cx_copo or 0, qtd_1500ml or 0, f"R$ {total:.2f}")
            self.tree_marca.insert("", "end", values=valores)

        self.lbl_total_marca.config(text=f"Total Geral: R$ {total_geral:.2f}")

    def gerar_relatorio_parceiro(self) -> None:
        parceiro = self.combo_parceiro.get()
        if not parceiro:
            messagebox.showwarning("Atenção", "Selecione um parceiro!")
            return

        parceiro_id = int(parceiro.split(" - ")[0])
        data_inicio = self._parse_date(self.entry_parceiro_inicio.get())
        data_fim = self._parse_date(self.entry_parceiro_fim.get())

        for item in self.tree_parceiro.get_children():
            self.tree_parceiro.delete(item)

        total_geral = 0.0
        for row in self._repo.relatorio_por_parceiro(parceiro_id, data_inicio, data_fim):
            nome, data, qtd_20l, qtd_10l, qtd_cx_copo, qtd_1500ml, val_20l, val_10l, val_copo, val_1500 = row
            total = (qtd_20l or 0) * (val_20l or 0) + (qtd_10l or 0) * (val_10l or 0) + (qtd_cx_copo or 0) * (val_copo or 0) + (qtd_1500ml or 0) * (val_1500 or 0)
            total_geral += total
            data_format = datetime.strptime(data, "%Y-%m-%d").strftime("%d/%m/%Y")
            valores = (nome, data_format, qtd_20l or 0, qtd_10l or 0, qtd_cx_copo or 0, qtd_1500ml or 0, f"R$ {total:.2f}")
            self.tree_parceiro.insert("", "end", values=valores)

        self.lbl_total_parceiro.config(text=f"Total a Receber: R$ {total_geral:.2f}")

    def exportar_relatorio(self, tipo: str) -> None:
        messagebox.showinfo("Info", f"Exportação de relatório de {tipo} será implementada")

