#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Página Inicial
--------------
Apresenta uma introdução ao sistema.
"""

import tkinter as tk
from tkinter import ttk
import datetime


class HomeView(ttk.Frame):
    """Página inicial do sistema."""

    def __init__(self, parent):
        super().__init__(parent)
        self._criar_widgets()

    def _criar_widgets(self):
        ttk.Label(
            self,
            text="Bem-vindo ao Sistema de Gestão de Parceiros",
            font=("Segoe UI", 16, "bold"),
        ).pack(pady=20)

        texto = (
            "Este aplicativo facilita o controle de parceiros, lojas e comprovantes "
            "de entrega. Utilize o menu lateral para navegar pelas funcionalidades."
        )
        ttk.Label(self, text=texto, wraplength=600, justify="center").pack(pady=10)

        ano = datetime.datetime.now().year
        ttk.Label(self, text=f"© {ano} Sistema de Gestão").pack(pady=10)