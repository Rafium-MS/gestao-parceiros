#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tela de Login
-------------
Permite a autenticação do usuário.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging


class LoginWindow(tk.Tk):
    """Janela de login da aplicação."""

    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)
        self.title("Login")
        self.resizable(False, False)
        self.user = None
        self._criar_widgets()
        self.protocol("WM_DELETE_WINDOW", self._sair)

    def _criar_widgets(self):
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Usuário:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Label(frame, text="Senha:").grid(row=1, column=0, sticky=tk.W, pady=5)

        self.entry_user = ttk.Entry(frame)
        self.entry_user.grid(row=0, column=1, pady=5)

        self.entry_pass = ttk.Entry(frame, show="*")
        self.entry_pass.grid(row=1, column=1, pady=5)

        btn = ttk.Button(frame, text="Entrar", command=self._login)
        btn.grid(row=2, column=0, columnspan=2, pady=10)

    def _login(self):
        username = self.entry_user.get().strip()
        password = self.entry_pass.get().strip()

        self.db_manager.execute(
            "SELECT password FROM users WHERE username=?", (username,)
        )
        row = self.db_manager.fetchone()
        if row and row[0] == password:
            self.logger.info(f"Usuário '{username}' autenticado")
            self.user = username
            self.destroy()
        else:
            self.logger.warning(f"Falha de login para '{username}'")
            messagebox.showerror("Erro", "Usuário ou senha inválidos")

    def _sair(self):
        self.logger.info("Janela de login fechada")
        self.destroy()