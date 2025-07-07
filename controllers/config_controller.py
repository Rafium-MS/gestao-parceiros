#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Controlador de Configurações
---------------------------
Gerencia o carregamento e salvamento das opções do arquivo config.ini.
"""

import configparser
import logging
from pathlib import Path


class ConfigController:
    """Controlador para manipular configurações do sistema."""

    def __init__(self, config_path="config.ini"):
        self.config_path = Path(config_path)
        self.logger = logging.getLogger(__name__)
        self.config = configparser.ConfigParser()
        self.load_config()

    def load_config(self):
        """Carrega as configurações a partir do arquivo."""
        if self.config_path.exists():
            self.config.read(self.config_path)
        else:
            self.logger.warning(f"Arquivo de configuração {self.config_path} não encontrado.")

    def get_config(self):
        """Retorna o objeto ConfigParser atual."""
        return self.config

    def update_option(self, section, option, value):
        """Atualiza uma opção em memória."""
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, option, value)

    def validate_config(self):
        """Realiza validações básicas antes de salvar."""
        if not self.config.get("DATABASE", "path", fallback=""):
            return False, "Caminho do banco de dados não pode ficar vazio."
        return True, "Configurações válidas"

    def save_config(self):
        """Salva as configurações no arquivo."""
        valid, msg = self.validate_config()
        if not valid:
            return False, msg
        try:
            with self.config_path.open("w") as f:
                self.config.write(f)
            self.logger.info("Configurações salvas com sucesso")
            return True, "Configurações salvas com sucesso."
        except Exception as e:
            self.logger.error(f"Erro ao salvar configurações: {e}")
            return False, str(e)