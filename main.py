"""Entry point for the gestão de parceiros application."""

from __future__ import annotations

from projeto.controllers.base_controller import BaseController


def main() -> None:
    """Bootstraps the graphical application."""
    controller = BaseController()
    controller.initialise_demo_content()
    controller.run()


if __name__ == "__main__":
    main()
