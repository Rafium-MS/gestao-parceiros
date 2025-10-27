"""Base controller responsável por iniciar a aplicação gráfica."""

from __future__ import annotations

import logging
import tkinter as tk

from views.main_window import SistemaEntregas


class BaseController:
    """Inicializa a janela principal e executa o loop da aplicação."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.logger.info("Inicializando controlador base")

        self.root = tk.Tk()
        self.app = SistemaEntregas(self.root)

    def run(self) -> None:
        self.logger.info("Executando loop principal da aplicação")
        self.root.mainloop()
