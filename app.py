#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Sistema de Gestão de Parceiros
----------------------------
Aplicação para gerenciamento de parceiros, lojas, comprovantes de entrega e relatórios.

Desenvolvido por: [Seu Nome]
Versão: 1.0
"""

import os
import sys
import tkinter as tk
import configparser
from tkinter import messagebox

# Adicionar diretórios ao path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Importar componentes
from views.main_window import MainWindow
from database.db_manager import DatabaseManager
from utils.logger import setup_logger


def check_dependencies():
    """Verifica se todas as dependências estão instaladas."""
    try:
        import PIL
        import sqlite3
        import pytesseract
        import pdf2image
        return True
    except ImportError as e:
        messagebox.showerror("Erro de Dependência",
                             f"Falta biblioteca: {str(e)}.\n"
                             "Instale as dependências usando: pip install -r requirements.txt")
        return False


def load_config():
    """Carrega as configurações do arquivo config.ini."""
    config = configparser.ConfigParser()

    # Verificar se o arquivo de configuração existe
    if not os.path.exists('config.ini'):
        # Criar configuração padrão
        config['DATABASE'] = {
            'path': 'database/gestao_parceiros.db'
        }
        config['COMPROVANTES'] = {
            'path': 'comprovantes',
            'allowed_extensions': '.png,.jpg,.jpeg,.pdf'
        }
        config['LOGS'] = {
            'path': 'logs',
            'level': 'INFO'
        }

        # Salvar arquivo de configuração
        with open('config.ini', 'w') as config_file:
            config.write(config_file)
    else:
        config.read('config.ini')

    return config


def setup_directories(config):
    """Configura os diretórios necessários."""
    # Criar diretório de comprovantes se não existir
    comprovantes_dir = config['COMPROVANTES']['path']
    if not os.path.exists(comprovantes_dir):
        os.makedirs(comprovantes_dir)

    # Criar diretório de logs se não existir
    logs_dir = config['LOGS']['path']
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)


def main():
    """Função principal que inicia a aplicação."""
    # Verificar dependências
    if not check_dependencies():
        return

    # Carregar configurações
    config = load_config()

    # Configurar diretórios
    setup_directories(config)

    # Configurar logger
    logger = setup_logger(config['LOGS']['path'], config['LOGS']['level'])
    logger.info("Iniciando aplicação")

    # Inicializar banco de dados
    db_manager = DatabaseManager(config['DATABASE']['path'])
    db_manager.setup_database()

    # Inicializar aplicação Tkinter
    root = tk.Tk()
    app = MainWindow(root, db_manager, config)

    # Configurar janela principal
    root.title("Sistema de Gestão de Parceiros")
    root.geometry("1200x700")
    root.minsize(1000, 600)

    # Iniciar o loop principal
    logger.info("Interface principal carregada")
    root.mainloop()

    # Fechar conexão com o banco de dados ao sair
    db_manager.close_connection()
    logger.info("Aplicação encerrada")


if __name__ == "__main__":
    main()