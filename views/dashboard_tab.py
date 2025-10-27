"""Dashboard tab widgets and behaviour."""

from __future__ import annotations

import logging
from datetime import datetime
import tkinter as tk
from tkinter import ttk

from models.repositories import ComprovantesRepository, LojasRepository, ParceirosRepository


logger = logging.getLogger(__name__)

class DashboardTab:
    """Build and refresh the dashboard tab."""

    def __init__(
        self,
        notebook: ttk.Notebook,
        parceiros_repo: ParceirosRepository,
        lojas_repo: LojasRepository,
        comprovantes_repo: ComprovantesRepository,
    ) -> None:
        self._parceiros_repo = parceiros_repo
        self._lojas_repo = lojas_repo
        self._comprovantes_repo = comprovantes_repo

        self.frame = tk.Frame(notebook, bg="white")
        notebook.add(self.frame, text="📊 Dashboard")

        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        title = tk.Label(
            self.frame,
            text="Dashboard - Visão Geral",
            font=("Arial", 16, "bold"),
            bg="white",
        )
        title.pack(pady=20)

        cards_frame = tk.Frame(self.frame, bg="white")
        cards_frame.pack(fill="both", expand=True, padx=20, pady=10)
        cards_frame.grid_columnconfigure(0, weight=1)
        cards_frame.grid_columnconfigure(1, weight=1)
        cards_frame.grid_columnconfigure(2, weight=1)

        self._cards_frame = cards_frame
        self._cards_columns = 0

        card1 = tk.Frame(cards_frame, bg="#3498db", relief="raised", borderwidth=2)
        tk.Label(
            card1,
            text="Parceiros com Entregas",
            font=("Arial", 12, "bold"),
            bg="#3498db",
            fg="white",
        ).pack(pady=10)
        self.lbl_parceiros_enviaram = tk.Label(
            card1,
            text="0 / 0",
            font=("Arial", 24, "bold"),
            bg="#3498db",
            fg="white",
        )
        self.lbl_parceiros_enviaram.pack(pady=10)

        card2 = tk.Frame(cards_frame, bg="#2ecc71", relief="raised", borderwidth=2)
        tk.Label(
            card2,
            text="Relatórios Preenchidos",
            font=("Arial", 12, "bold"),
            bg="#2ecc71",
            fg="white",
        ).pack(pady=10)
        self.lbl_percentual_relatorios = tk.Label(
            card2,
            text="0%",
            font=("Arial", 24, "bold"),
            bg="#2ecc71",
            fg="white",
        )
        self.lbl_percentual_relatorios.pack(pady=10)

        card3 = tk.Frame(cards_frame, bg="#e74c3c", relief="raised", borderwidth=2)
        tk.Label(
            card3,
            text="Total de Lojas",
            font=("Arial", 12, "bold"),
            bg="#e74c3c",
            fg="white",
        ).pack(pady=10)
        self.lbl_total_lojas = tk.Label(
            card3,
            text="0",
            font=("Arial", 24, "bold"),
            bg="#e74c3c",
            fg="white",
        )
        self.lbl_total_lojas.pack(pady=10)

        self._cards = (card1, card2, card3)
        self._reflow_cards(3)

        self.frame.bind("<Configure>", self._handle_resize)

        list_frame = tk.LabelFrame(
            self.frame,
            text="Farol de Parceiros",
            font=("Arial", 12, "bold"),
            bg="white",
        )
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)

        columns = ("Parceiro", "Status", "Última Entrega")
        self.tree_dashboard = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)
        for column in columns:
            self.tree_dashboard.heading(column, text=column)
        self.tree_dashboard.column("Parceiro", width=300)
        self.tree_dashboard.column("Status", width=150)
        self.tree_dashboard.column("Última Entrega", width=150)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree_dashboard.yview)
        self.tree_dashboard.configure(yscrollcommand=scrollbar.set)

        self.tree_dashboard.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        list_frame.bind("<Configure>", lambda event: self._auto_size_tree())

        btn_frame = tk.Frame(self.frame, bg="white")
        btn_frame.pack(pady=10)

        tk.Button(
            btn_frame,
            text="🔄 Atualizar Dashboard",
            font=("Arial", 11),
            bg="#3498db",
            fg="white",
            command=self.refresh,
            padx=20,
            pady=10,
        ).pack()

    def _handle_resize(self, event: tk.Event) -> None:
        width = event.width
        if width < 640:
            columns = 1
        elif width < 960:
            columns = 2
        else:
            columns = 3
        if columns != self._cards_columns:
            self._reflow_cards(columns)

    def _reflow_cards(self, columns: int) -> None:
        for card in self._cards:
            card.grid_forget()

        for idx, card in enumerate(self._cards):
            row = idx // columns
            col = idx % columns
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

        for col in range(columns):
            self._cards_frame.grid_columnconfigure(col, weight=1)

        self._cards_columns = columns

    def _auto_size_tree(self) -> None:
        total_width = self.tree_dashboard.winfo_width()
        if total_width <= 0:
            return
        self.tree_dashboard.column("Parceiro", width=int(total_width * 0.5))
        self.tree_dashboard.column("Status", width=int(total_width * 0.25))
        self.tree_dashboard.column("Última Entrega", width=int(total_width * 0.25))

    def refresh(self) -> None:
        total_parceiros = self._parceiros_repo.count_all()
        parceiros_enviaram = self._comprovantes_repo.count_distinct_parceiros()
        total_lojas = self._lojas_repo.count_all()

        self.lbl_parceiros_enviaram.config(text=f"{parceiros_enviaram} / {total_parceiros}")
        self.lbl_total_lojas.config(text=str(total_lojas))

        percentual = (parceiros_enviaram / total_parceiros * 100) if total_parceiros else 0
        self.lbl_percentual_relatorios.config(text=f"{percentual:.0f}%")

        for item in self.tree_dashboard.get_children():
            self.tree_dashboard.delete(item)

        for nome, status, ultima in self._parceiros_repo.list_with_last_delivery():
            if ultima != "Sem entregas":
                try:
                    ultima = datetime.strptime(ultima, "%Y-%m-%d").strftime("%d/%m/%Y")
                except ValueError as exc:
                    logger.error(
                        "Erro ao converter data da última entrega do parceiro %s: %s",
                        nome,
                        exc,
                    )
            self.tree_dashboard.insert("", "end", values=(nome, status, ultima))

        self._auto_size_tree()

