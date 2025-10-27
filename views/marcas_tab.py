"""Tab responsável pela gestão de marcas."""

from __future__ import annotations

import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk

from models.repositories import MarcasRepository


class MarcasTab:
    def __init__(
        self,
        notebook: ttk.Notebook,
        marcas_repo: MarcasRepository,
        on_change: callable | None = None,
    ) -> None:
        self._repo = marcas_repo
        self._on_change = on_change

        self.frame = tk.Frame(notebook, bg="white")
        notebook.add(self.frame, text="🏢 Marcas")

        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        cadastro_frame = tk.LabelFrame(
            self.frame,
            text="Cadastro de Marca",
            font=("Arial", 11, "bold"),
            bg="white",
        )
        cadastro_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(cadastro_frame, text="Nome da Marca:", bg="white").grid(
            row=0, column=0, padx=10, pady=5, sticky="w"
        )
        self.entry_nome = tk.Entry(cadastro_frame, width=40)
        self.entry_nome.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(cadastro_frame, text="Código Disagua:", bg="white").grid(
            row=1, column=0, padx=10, pady=5, sticky="w"
        )
        self.entry_codigo = tk.Entry(cadastro_frame, width=40)
        self.entry_codigo.grid(row=1, column=1, padx=10, pady=5)

        btn_frame = tk.Frame(cadastro_frame, bg="white")
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10)

        tk.Button(
            btn_frame,
            text="Salvar Marca",
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
            text="Marcas Cadastradas",
            font=("Arial", 11, "bold"),
            bg="white",
        )
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)

        columns = ("ID", "Nome", "Código Disagua")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=12)
        for column in columns:
            self.tree.heading(column, text=column)
            self.tree.column(column, width=200)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        action_frame = tk.Frame(self.frame, bg="white")
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

    def set_on_change(self, callback: callable | None) -> None:
        self._on_change = callback

    def salvar(self) -> None:
        nome = self.entry_nome.get().strip()
        codigo = self.entry_codigo.get().strip()

        if not nome:
            messagebox.showwarning("Atenção", "Informe o nome da marca!")
            return

        try:
            self._repo.add(nome, codigo or None)
        except sqlite3.IntegrityError:
            messagebox.showerror("Erro", "Código Disagua já cadastrado!")
            return

        messagebox.showinfo("Sucesso", "Marca cadastrada com sucesso!")
        self.limpar()
        self.refresh()
        if self._on_change:
            self._on_change()

    def limpar(self) -> None:
        self.entry_nome.delete(0, tk.END)
        self.entry_codigo.delete(0, tk.END)

    def refresh(self) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)

        for row in self._repo.list_all():
            codigo = row[2] if row[2] else "—"
            self.tree.insert("", "end", values=(row[0], row[1], codigo))

    def editar(self) -> None:
        messagebox.showinfo("Info", "Função de edição será implementada")

    def excluir(self) -> None:
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Atenção", "Selecione uma marca!")
            return

        if not messagebox.askyesno("Confirmar", "Deseja realmente excluir esta marca?"):
            return

        item = self.tree.item(selected[0])
        marca_id = item["values"][0]

        self._repo.delete(marca_id)
        messagebox.showinfo("Sucesso", "Marca excluída!")
        self.refresh()
        if self._on_change:
            self._on_change()

