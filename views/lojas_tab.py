"""Tab de gerenciamento de lojas."""

from __future__ import annotations

import logging
import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk

from models.repositories import LojasRepository, MarcasRepository


logger = logging.getLogger(__name__)


class LojasTab:
    def __init__(
        self,
        notebook: ttk.Notebook,
        lojas_repo: LojasRepository,
        marcas_repo: MarcasRepository,
        on_change: callable | None = None,
    ) -> None:
        self._repo = lojas_repo
        self._marcas_repo = marcas_repo
        self._on_change = on_change

        self.frame = tk.Frame(notebook, bg="white")
        notebook.add(self.frame, text="🏪 Lojas")

        self._build_ui()
        self.update_marcas()
        self.refresh()

    def _build_ui(self) -> None:
        canvas = tk.Canvas(self.frame, bg="white")
        scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="white")

        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        cadastro_frame = tk.LabelFrame(
            scrollable_frame,
            text="Cadastro de Loja",
            font=("Arial", 11, "bold"),
            bg="white",
        )
        cadastro_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(cadastro_frame, text="Marca:", bg="white").grid(
            row=0, column=0, padx=10, pady=5, sticky="w"
        )
        self.combo_marca = ttk.Combobox(cadastro_frame, width=37, state="readonly")
        self.combo_marca.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(cadastro_frame, text="Nome da Loja:", bg="white").grid(
            row=1, column=0, padx=10, pady=5, sticky="w"
        )
        self.entry_nome = tk.Entry(cadastro_frame, width=40)
        self.entry_nome.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(cadastro_frame, text="Código Disagua:", bg="white").grid(
            row=2, column=0, padx=10, pady=5, sticky="w"
        )
        self.entry_codigo = tk.Entry(cadastro_frame, width=40)
        self.entry_codigo.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(cadastro_frame, text="Local de Entrega:", bg="white").grid(
            row=3, column=0, padx=10, pady=5, sticky="w"
        )
        self.entry_local = tk.Entry(cadastro_frame, width=40)
        self.entry_local.grid(row=3, column=1, padx=10, pady=5)

        tk.Label(cadastro_frame, text="Município:", bg="white").grid(
            row=4, column=0, padx=10, pady=5, sticky="w"
        )
        self.entry_municipio = tk.Entry(cadastro_frame, width=40)
        self.entry_municipio.grid(row=4, column=1, padx=10, pady=5)

        tk.Label(cadastro_frame, text="Estado:", bg="white").grid(
            row=5, column=0, padx=10, pady=5, sticky="w"
        )
        self.entry_estado = tk.Entry(cadastro_frame, width=40)
        self.entry_estado.grid(row=5, column=1, padx=10, pady=5)

        tk.Label(cadastro_frame, text="Valor 20L (R$):", bg="white").grid(
            row=0, column=2, padx=10, pady=5, sticky="w"
        )
        self.entry_valor_20l = tk.Entry(cadastro_frame, width=20)
        self.entry_valor_20l.grid(row=0, column=3, padx=10, pady=5)

        tk.Label(cadastro_frame, text="Valor 10L (R$):", bg="white").grid(
            row=1, column=2, padx=10, pady=5, sticky="w"
        )
        self.entry_valor_10l = tk.Entry(cadastro_frame, width=20)
        self.entry_valor_10l.grid(row=1, column=3, padx=10, pady=5)

        tk.Label(cadastro_frame, text="Valor Cx Copo (R$):", bg="white").grid(
            row=2, column=2, padx=10, pady=5, sticky="w"
        )
        self.entry_valor_cx_copo = tk.Entry(cadastro_frame, width=20)
        self.entry_valor_cx_copo.grid(row=2, column=3, padx=10, pady=5)

        tk.Label(cadastro_frame, text="Valor 1500ml (R$):", bg="white").grid(
            row=3, column=2, padx=10, pady=5, sticky="w"
        )
        self.entry_valor_1500ml = tk.Entry(cadastro_frame, width=20)
        self.entry_valor_1500ml.grid(row=3, column=3, padx=10, pady=5)

        btn_frame = tk.Frame(cadastro_frame, bg="white")
        btn_frame.grid(row=6, column=0, columnspan=4, pady=10)

        tk.Button(
            btn_frame,
            text="Salvar Loja",
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
            text="Lojas Cadastradas",
            font=("Arial", 11, "bold"),
            bg="white",
        )
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)

        columns = ("ID", "Marca", "Nome", "Município", "Estado", "Valor 20L")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)
        for column in columns:
            self.tree.heading(column, text=column)
        self.tree.column("ID", width=50)
        self.tree.column("Marca", width=150)
        self.tree.column("Nome", width=200)
        self.tree.column("Município", width=150)
        self.tree.column("Estado", width=80)
        self.tree.column("Valor 20L", width=100)

        scrollbar_tree = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar_tree.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar_tree.pack(side="right", fill="y")

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

    def set_on_change(self, callback: callable | None) -> None:
        self._on_change = callback

    def update_marcas(self) -> None:
        self.combo_marca["values"] = list(self._marcas_repo.combo_values())

    def salvar(self) -> None:
        marca = self.combo_marca.get()
        if not marca:
            messagebox.showwarning("Atenção", "Selecione uma marca!")
            return

        try:
            marca_id = int(marca.split(" - ")[0])
        except ValueError as exc:
            logger.error("Erro ao converter ID da marca selecionada: %s", exc)
            messagebox.showerror("Erro", "Marca inválida!")
            return

        nome = self.entry_nome.get().strip()
        codigo = self.entry_codigo.get().strip()
        local = self.entry_local.get().strip()
        municipio = self.entry_municipio.get().strip()
        estado = self.entry_estado.get().strip()

        if not nome:
            messagebox.showwarning("Atenção", "Informe o nome da loja!")
            return

        def parse_float(value: str) -> float | None:
            value = value.strip()
            if not value:
                return None
            return float(value.replace(",", "."))

        try:
            self._repo.add(
                marca_id,
                nome,
                codigo or None,
                local,
                municipio,
                estado,
                parse_float(self.entry_valor_20l.get()),
                parse_float(self.entry_valor_10l.get()),
                parse_float(self.entry_valor_cx_copo.get()),
                parse_float(self.entry_valor_1500ml.get()),
            )
        except ValueError as exc:
            logger.error("Erro ao converter valores numéricos da loja: %s", exc)
            messagebox.showerror("Erro", "Valores numéricos inválidos!")
            return
        except sqlite3.IntegrityError as exc:
            logger.error(
                "Erro ao salvar loja devido a código Disagua duplicado: %s", exc
            )
            messagebox.showerror("Erro", "Código Disagua já cadastrado!")
            return

        messagebox.showinfo("Sucesso", "Loja cadastrada com sucesso!")
        self.limpar()
        self.refresh()
        if self._on_change:
            self._on_change()

    def limpar(self) -> None:
        self.combo_marca.set("")
        for entry in (
            self.entry_nome,
            self.entry_codigo,
            self.entry_local,
            self.entry_municipio,
            self.entry_estado,
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
            messagebox.showwarning("Atenção", "Selecione uma loja!")
            return

        if not messagebox.askyesno("Confirmar", "Deseja realmente excluir esta loja?"):
            return

        item = self.tree.item(selected[0])
        loja_id = item["values"][0]

        self._repo.delete(loja_id)
        messagebox.showinfo("Sucesso", "Loja excluída!")
        self.refresh()
        if self._on_change:
            self._on_change()

