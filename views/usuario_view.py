#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interface de Usuários
--------------------
Tela para gerenciamento de usuários do sistema.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging

from controllers.usuario_controller import UsuarioController
from utils.tooltip import ToolTip
from utils.style import configurar_estilos_modernos


class UsuarioView(ttk.Frame):
    """Interface gráfica para gerenciamento de usuários."""

    def __init__(self, parent, db_manager):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.controller = UsuarioController(db_manager)
        configurar_estilos_modernos()
        self.usuario_atual_id = None

        self._criar_widgets()
        self._configurar_eventos()
        self._carregar_usuarios()

    def _criar_widgets(self):
        self.frame_form = ttk.LabelFrame(self, text="Cadastro de Usuários")
        self.frame_form.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(self.frame_form, text="Usuário:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.entrada_usuario = ttk.Entry(self.frame_form, width=30)
        self.entrada_usuario.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.frame_form, text="Senha:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.entrada_senha = ttk.Entry(self.frame_form, width=30, show="*")
        self.entrada_senha.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self.frame_form, text="Perfil:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.combo_role = ttk.Combobox(self.frame_form, state="readonly")
        self.combo_role.grid(row=2, column=1, padx=5, pady=5)

        self.frame_botoes = ttk.Frame(self.frame_form)
        self.frame_botoes.grid(row=3, column=0, columnspan=2, pady=10)

        self.btn_adicionar = ttk.Button(self.frame_botoes, text="Adicionar", command=self._adicionar_usuario)
        self.btn_adicionar.pack(side=tk.LEFT, padx=5)

        self.btn_editar = ttk.Button(self.frame_botoes, text="Salvar Edição", command=self._editar_usuario, state=tk.DISABLED)
        self.btn_editar.pack(side=tk.LEFT, padx=5)

        self.btn_excluir = ttk.Button(self.frame_botoes, text="Excluir", command=self._excluir_usuario, state=tk.DISABLED)
        self.btn_excluir.pack(side=tk.LEFT, padx=5)

        self.btn_limpar = ttk.Button(self.frame_botoes, text="Limpar", command=self._limpar_form)
        self.btn_limpar.pack(side=tk.LEFT, padx=5)

        self.frame_lista = ttk.Frame(self)
        self.frame_lista.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        colunas = ("id", "username", "role")
        self.treeview = ttk.Treeview(self.frame_lista, columns=colunas, show="headings", selectmode="browse")
        self.treeview.heading("id", text="ID")
        self.treeview.heading("username", text="Usuário")
        self.treeview.heading("role", text="Perfil")

        self.treeview.column("id", width=50, minwidth=50)
        self.treeview.column("username", width=200, minwidth=150)
        self.treeview.column("role", width=120, minwidth=100)

        scrollbar = ttk.Scrollbar(self.frame_lista, orient=tk.VERTICAL, command=self.treeview.yview)
        self.treeview.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.treeview.pack(fill=tk.BOTH, expand=True)

        style = ttk.Style()
        style.map("Treeview", background=[("selected", "#347083")])
        style.configure("Treeview", rowheight=25)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.configure("Treeview", font=("Segoe UI", 10))

        self.treeview.tag_configure('oddrow', background='#f9f9f9')
        self.treeview.tag_configure('evenrow', background='#ffffff')

        ToolTip(self.btn_adicionar, "Adiciona um novo usuário")
        ToolTip(self.btn_editar, "Salva alterações no usuário selecionado")
        ToolTip(self.btn_excluir, "Remove o usuário selecionado")
        ToolTip(self.btn_limpar, "Limpa o formulário")

    def _configurar_eventos(self):
        self.treeview.bind("<<TreeviewSelect>>", self._on_treeview_select)
        self.bind("<Escape>", lambda event: self._limpar_form())

    def _obter_dados_form(self):
        senha = self.entrada_senha.get().strip()
        return {
            "username": self.entrada_usuario.get().strip(),
            "password": senha if senha else None,
            "role_id": self._role_id_por_nome(self.combo_role.get()),
        }

    def _limpar_form(self):
        self.entrada_usuario.delete(0, tk.END)
        self.entrada_senha.delete(0, tk.END)
        self.combo_role.set("")
        self.usuario_atual_id = None
        self.btn_adicionar.config(state=tk.NORMAL)
        self.btn_editar.config(state=tk.DISABLED)
        self.btn_excluir.config(state=tk.DISABLED)
        for item in self.treeview.selection():
            self.treeview.selection_remove(item)

    def _carregar_usuarios(self):
        self.roles = {nome: role_id for role_id, nome in self.controller.listar_roles()}
        self.combo_role['values'] = list(self.roles.keys())

        usuarios = self.controller.listar_usuarios()
        for item in self.treeview.get_children():
            self.treeview.delete(item)
        for idx, usuario in enumerate(usuarios):
            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            self.treeview.insert("", tk.END, values=usuario, tags=(tag,))

    def _role_id_por_nome(self, nome):
        return self.roles.get(nome)

    def _on_treeview_select(self, event=None):
        selecao = self.treeview.selection()
        if selecao:
            item = self.treeview.item(selecao[0])
            valores = item['values']
            self.usuario_atual_id = valores[0]
            self.entrada_usuario.delete(0, tk.END)
            self.entrada_usuario.insert(0, valores[1])
            self.entrada_senha.delete(0, tk.END)
            self.combo_role.set(valores[2])
            self.btn_adicionar.config(state=tk.DISABLED)
            self.btn_editar.config(state=tk.NORMAL)
            self.btn_excluir.config(state=tk.NORMAL)

    def _adicionar_usuario(self):
        dados = self._obter_dados_form()
        ok, msg = self.controller.adicionar_usuario(dados)
        if ok:
            messagebox.showinfo("Sucesso", msg)
            self._limpar_form()
            self._carregar_usuarios()
        else:
            messagebox.showerror("Erro", msg)

    def _editar_usuario(self):
        if not self.usuario_atual_id:
            messagebox.showwarning("Aviso", "Nenhum usuário selecionado")
            return
        dados = self._obter_dados_form()
        ok, msg = self.controller.editar_usuario(self.usuario_atual_id, dados)
        if ok:
            messagebox.showinfo("Sucesso", msg)
            self._limpar_form()
            self._carregar_usuarios()
        else:
            messagebox.showerror("Erro", msg)

    def _excluir_usuario(self):
        if not self.usuario_atual_id:
            messagebox.showwarning("Aviso", "Nenhum usuário selecionado")
            return
        if messagebox.askyesno("Confirmar", "Deseja realmente excluir o usuário selecionado?"):
            ok, msg = self.controller.excluir_usuario(self.usuario_atual_id)
            if ok:
                messagebox.showinfo("Sucesso", msg)
                self._limpar_form()
                self._carregar_usuarios()
            else:
                messagebox.showerror("Erro", msg)

    def focus_nome(self):
        self.entrada_usuario.focus_set()