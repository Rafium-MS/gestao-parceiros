"""Simple command-line view for the application."""

from __future__ import annotations

from typing import Iterable


class MainWindow:
    """Text-based view responsible for presenting options to the user."""

    def display_menu(self, options: Iterable[str]) -> str:
        """Render the menu and return the option selected by the user."""
        menu_lines = ["Selecione uma opção:"]
        menu_lines.extend(f"- {option}" for option in options)
        menu_text = "\n".join(menu_lines)
        print(menu_text)
        # In a real application user input would be captured here.
        return ""

    def show_message(self, message: str) -> None:
        """Display a message to the user."""
        print(message)
