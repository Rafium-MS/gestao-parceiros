"""Entry point for the gestão de parceiros application."""

from __future__ import annotations

import logging

from config.logging_config import setup_logging
from controllers.base_controller import BaseController

logger = logging.getLogger(__name__)


def main() -> None:
    """Bootstraps the graphical application."""
    setup_logging()
    logger.info("Iniciando aplicação Gestão de Parceiros")

    controller = BaseController()
    controller.run()


if __name__ == "__main__":
    main()
