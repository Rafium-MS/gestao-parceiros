#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interface de Configurações
-------------------------
Permite editar as preferências salvas em config.ini.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from utils.tooltip import ToolTip
from utils.style import configurar_estilos_modernos


class ConfigView(tk.Toplevel):
    """Janela para edição das configurações do sistema."""

    def __init__(self, master, controller):
        super().__init__(master)
        self.title("Configurações")
        self.resizable(False, False)
        self.controller = controller
        self.entries = {}
        configurar_estilos_modernos()
        self._criar_widgets()
        self._carregar_valores()
        self.grab_set()
        self.transient(master)

    def _criar_widgets(self):
        """Cria os campos baseados nas seções da configuração."""
        config = self.controller.get_config()
        for section in config.sections():
            frame = ttk.LabelFrame(self, text=section)
            frame.pack(fill=tk.X, padx=10, pady=5)
            for option in config[section]:
                row = ttk.Frame(frame)
                row.pack(fill=tk.X, pady=2, padx=5)
                ttk.Label(row, text=option).pack(side=tk.LEFT)
                entry = ttk.Entry(row, width=50)
                entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
                self.entries[(section, option)] = entry
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)
        btn_salvar = ttk.Button(btn_frame, text="Salvar", command=self._salvar)
        btn_salvar.pack(side=tk.LEFT, padx=5)
        ToolTip(btn_salvar, "Salva as alterações no arquivo de configuração.")

        ttk.Button(btn_frame, text="Fechar", command=self.destroy).pack(side=tk.LEFT, padx=5)

    def _carregar_valores(self):
        """Preenche os campos com os valores atuais."""
        config = self.controller.get_config()
        for (section, option), entry in self.entries.items():
            entry.delete(0, tk.END)
            entry.insert(0, config.get(section, option, fallback=""))

    def _salvar(self):
        """Salva as alterações no arquivo de configuração."""
        for (section, option), entry in self.entries.items():
            self.controller.update_option(section, option, entry.get())
        ok, msg = self.controller.save_config()
        if ok:
            messagebox.showinfo("Configurações", msg)
            self.destroy()
        else:
            messagebox.showerror("Erro", msg)