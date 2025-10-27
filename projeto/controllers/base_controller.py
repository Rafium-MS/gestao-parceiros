"""Base controller shared by the application workflows."""

from __future__ import annotations

from projeto.views.main_window import MainWindow


class BaseController:
    """Provide convenience helpers for derived controllers."""

    def __init__(self, view: MainWindow | None = None) -> None:
        self.view = view or MainWindow()

    def show_startup_message(self) -> None:
        """Present a welcome message using the configured view."""
        self.view.show_message("Bem-vindo ao sistema de gestão de parceiros!")
