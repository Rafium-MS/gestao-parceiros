"""Entry point for the gestão de parceiros application."""

from __future__ import annotations

from projeto.controllers.base_controller import BaseController
from projeto.utils import format_currency, validate_email


def main() -> None:
    """Bootstraps the minimal demo application."""
    controller = BaseController()
    controller.show_startup_message()

    sample_email = "contato@empresa.com"
    if validate_email(sample_email):
        controller.view.show_message(f"Email '{sample_email}' validado com sucesso!")

    controller.view.show_message(f"Exemplo de formatação monetária: {format_currency(1234.5)}")


if __name__ == "__main__":
    main()
