#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Logger
------
Configuração do sistema de logging para a aplicação.
"""

import os
import logging
from logging.handlers import RotatingFileHandler
import datetime


def setup_logger(log_dir, log_level='INFO'):
    """
    Configura o sistema de logging da aplicação.

    Args:
        log_dir (str): Diretório onde os logs serão salvos.
        log_level (str): Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL).

    Returns:
        logging.Logger: Logger configurado.
    """
    # Criar diretório de logs se não existir
    os.makedirs(log_dir, exist_ok=True)

    # Definir nome do arquivo de log com timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d")
    log_file = os.path.join(log_dir, f"gestao_entregas_{timestamp}.log")

    # Configurar nível de log
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        numeric_level = logging.INFO  # Padrão para INFO se nível inválido

    # Configurar formato do log
    log_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(fmt=log_format, datefmt=date_format)

    # Configurar logger raiz
    logger = logging.getLogger()
    logger.setLevel(numeric_level)

    # Limpar handlers existentes para evitar duplicação
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Handler para arquivo com rotação
    # Limita cada arquivo a 5MB e mantém até 10 arquivos de backup
    file_handler = RotatingFileHandler(
        log_file, maxBytes=5 * 1024 * 1024, backupCount=10, encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(numeric_level)
    logger.addHandler(file_handler)

    # Handler para console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(numeric_level)
    logger.addHandler(console_handler)

    # Log inicial
    logger.info("=" * 50)
    logger.info("Iniciando sistema de logs")
    logger.info(f"Nível de log: {log_level}")
    logger.info(f"Arquivo de log: {log_file}")

    return logger


def get_logger(name):
    """
    Obtém um logger para um módulo específico.

    Args:
        name (str): Nome do módulo (geralmente __name__).

    Returns:
        logging.Logger: Logger específico para o módulo.
    """
    return logging.getLogger(name)


class LogManager:
    """
    Gerenciador de logs que permite acessar e gerenciar arquivos de log.
    """

    @staticmethod
    def list_log_files(log_dir):
        """
        Lista todos os arquivos de log disponíveis.

        Args:
            log_dir (str): Diretório de logs.

        Returns:
            list: Lista de arquivos de log.
        """
        try:
            if not os.path.exists(log_dir):
                return []

            log_files = [f for f in os.listdir(log_dir) if f.endswith('.log')]
            return sorted(log_files, reverse=True)
        except Exception as e:
            logging.getLogger(__name__).error(f"Erro ao listar arquivos de log: {str(e)}")
            return []

    @staticmethod
    def read_log_file(log_dir, log_file, max_lines=500):
        """
        Lê as últimas linhas de um arquivo de log.

        Args:
            log_dir (str): Diretório de logs.
            log_file (str): Nome do arquivo de log.
            max_lines (int): Número máximo de linhas a retornar.

        Returns:
            str: Conteúdo do arquivo de log.
        """
        try:
            file_path = os.path.join(log_dir, log_file)
            if not os.path.exists(file_path):
                return f"Arquivo de log não encontrado: {log_file}"

            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Retornar as últimas N linhas
            return ''.join(lines[-max_lines:])
        except Exception as e:
            return f"Erro ao ler arquivo de log: {str(e)}"

    @staticmethod
    def clear_old_logs(log_dir, days_to_keep=30):
        """
        Remove logs antigos baseado na data de modificação.

        Args:
            log_dir (str): Diretório de logs.
            days_to_keep (int): Número de dias para manter os logs.

        Returns:
            int: Número de arquivos removidos.
        """
        try:
            if not os.path.exists(log_dir):
                return 0

            current_time = datetime.datetime.now()
            cutoff_time = current_time - datetime.timedelta(days=days_to_keep)
            cutoff_timestamp = cutoff_time.timestamp()

            removed_count = 0
            for filename in os.listdir(log_dir):
                if filename.endswith('.log'):
                    file_path = os.path.join(log_dir, filename)
                    file_timestamp = os.path.getmtime(file_path)

                    if file_timestamp < cutoff_timestamp:
                        os.remove(file_path)
                        removed_count += 1

            logging.getLogger(__name__).info(f"Limpeza de logs: {removed_count} arquivos removidos.")
            return removed_count
        except Exception as e:
            logging.getLogger(__name__).error(f"Erro ao limpar logs antigos: {str(e)}")
            return 0