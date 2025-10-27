"""Base controller shared by the application workflows."""

from __future__ import annotations

from projeto.utils import format_currency, validate_email
from projeto.views.main_window import MainWindow


class BaseController:
    """Provide convenience helpers for derived controllers."""

    def __init__(self, view: MainWindow | None = None) -> None:
        self.view = view or MainWindow()

    def initialise_demo_content(self) -> None:
        """Populate the interface with initial helper messages."""
        self.view.show_status("Bem-vindo ao sistema de gestão de parceiros!")

        sample_email = "contato@empresa.com"
        if validate_email(sample_email):
            self.view.append_log(f"Email '{sample_email}' validado com sucesso!")

        self.view.append_log(
            "Exemplo de formatação monetária: " + format_currency(1234.5)
        )

    def run(self) -> None:
        """Start the GUI application."""
        self.view.run()
