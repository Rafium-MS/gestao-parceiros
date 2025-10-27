"""Base controller responsável por iniciar a aplicação gráfica."""

from __future__ import annotations

import tkinter as tk

from views.main_window import SistemaEntregas


class BaseController:
    """Inicializa a janela principal e executa o loop da aplicação."""

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.app = SistemaEntregas(self.root)

    def run(self) -> None:
        self.root.mainloop()

