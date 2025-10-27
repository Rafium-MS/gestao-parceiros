"""Entry point for the gestão de parceiros application."""

from __future__ import annotations

from controllers.base_controller import BaseController


def main() -> None:
    """Bootstraps the graphical application."""
    controller = BaseController()
    controller.run()


if __name__ == "__main__":
    main()
