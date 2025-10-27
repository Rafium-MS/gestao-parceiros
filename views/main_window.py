"""Janela principal do sistema de gestão de entregas."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from models.database import init_database
from models.repositories import (
    ComprovantesRepository,
    LojasRepository,
    MarcasRepository,
    ParceiroLojaRepository,
    ParceirosRepository,
)
from views.comprovantes_tab import ComprovantesTab
from views.dashboard_tab import DashboardTab
from views.lojas_tab import LojasTab
from views.marcas_tab import MarcasTab
from views.parceiros_tab import ParceirosTab
from views.relatorios_tab import RelatoriosTab


class SistemaEntregas:
    def __init__(self, root: tk.Tk, db_path: str | None = None) -> None:
        self.root = root
        self.root.title("Sistema de Gerenciamento de Entregas - Água Mineral")
        self.root.geometry("1200x700")
        self.root.minsize(900, 600)
        self.root.configure(bg="#f0f0f0")
        self.root.rowconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)

        self.conn, _ = init_database(db_path)

        self.marcas_repo = MarcasRepository(self.conn)
        self.lojas_repo = LojasRepository(self.conn)
        self.parceiros_repo = ParceirosRepository(self.conn)
        self.parceiro_loja_repo = ParceiroLojaRepository(self.conn)
        self.comprovantes_repo = ComprovantesRepository(self.conn)

        self._build_main_layout()

    def _build_main_layout(self) -> None:
        header_frame = tk.Frame(self.root, bg="#2c3e50", height=60)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)

        title_label = tk.Label(
            header_frame,
            text="Sistema de Gerenciamento de Entregas",
            font=("Arial", 18, "bold"),
            bg="#2c3e50",
            fg="white",
        )
        title_label.pack(pady=15)

        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        main_frame.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)

        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill="both", expand=True)

        self.dashboard_tab = DashboardTab(
            self.notebook,
            parceiros_repo=self.parceiros_repo,
            lojas_repo=self.lojas_repo,
            comprovantes_repo=self.comprovantes_repo,
        )
        self.marcas_tab = MarcasTab(
            self.notebook,
            marcas_repo=self.marcas_repo,
            on_change=self._on_marcas_change,
        )
        self.lojas_tab = LojasTab(
            self.notebook,
            lojas_repo=self.lojas_repo,
            marcas_repo=self.marcas_repo,
            on_change=self._on_lojas_change,
        )
        self.parceiros_tab = ParceirosTab(
            self.notebook,
            parceiros_repo=self.parceiros_repo,
            lojas_repo=self.lojas_repo,
            vinculo_repo=self.parceiro_loja_repo,
            on_change=self._on_parceiros_change,
        )
        self.comprovantes_tab = ComprovantesTab(
            self.notebook,
            comprovantes_repo=self.comprovantes_repo,
            parceiros_repo=self.parceiros_repo,
            vinculo_repo=self.parceiro_loja_repo,
            on_change=self._on_comprovantes_change,
        )
        self.relatorios_tab = RelatoriosTab(
            self.notebook,
            comprovantes_repo=self.comprovantes_repo,
            marcas_repo=self.marcas_repo,
            parceiros_repo=self.parceiros_repo,
        )

    def _on_marcas_change(self) -> None:
        self.lojas_tab.update_marcas()
        self.relatorios_tab.update_marcas()

    def _on_lojas_change(self) -> None:
        self.dashboard_tab.refresh()
        self.parceiros_tab.carregar_lojas_vinculacao()
        self.comprovantes_tab.atualizar_lojas()

    def _on_parceiros_change(self) -> None:
        self.dashboard_tab.refresh()
        self.parceiros_tab.update_parceiros_combo()
        self.comprovantes_tab.refresh_parceiros()
        self.comprovantes_tab.atualizar_lojas()
        self.relatorios_tab.update_parceiros()

    def _on_comprovantes_change(self) -> None:
        self.dashboard_tab.refresh()

    def __del__(self) -> None:
        if hasattr(self, "conn"):
            self.conn.close()


if __name__ == "__main__":
    root = tk.Tk()
    app = SistemaEntregas(root)
    root.mainloop()

