import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime
import os

class SistemaEntregas:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Gerenciamento de Entregas - Água Mineral")
        self.root.geometry("1200x700")
        self.root.configure(bg='#f0f0f0')
        
        # Inicializar banco de dados
        self.init_database()
        
        # Criar interface
        self.create_widgets()
        
    def init_database(self):
        """Inicializa o banco de dados SQLite"""
        self.conn = sqlite3.connect('entregas.db')
        self.cursor = self.conn.cursor()
        
        # Tabela de Marcas
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS marcas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                codigo_disagua TEXT UNIQUE NOT NULL
            )
        ''')
        
        # Tabela de Lojas
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS lojas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                marca_id INTEGER,
                nome TEXT NOT NULL,
                codigo_disagua TEXT UNIQUE NOT NULL,
                local_entrega TEXT,
                municipio TEXT,
                estado TEXT,
                valor_20l REAL,
                valor_10l REAL,
                valor_cx_copo REAL,
                valor_1500ml REAL,
                FOREIGN KEY (marca_id) REFERENCES marcas(id)
            )
        ''')
        
        # Tabela de Parceiros
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS parceiros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cidade TEXT,
                estado TEXT,
                nome_parceiro TEXT NOT NULL,
                distribuidora TEXT,
                cnpj TEXT,
                telefone TEXT,
                email TEXT,
                dia_pagamento INTEGER,
                banco TEXT,
                agencia TEXT,
                conta TEXT,
                chave_pix TEXT,
                valor_20l REAL,
                valor_10l REAL,
                valor_cx_copo REAL,
                valor_1500ml REAL
            )
        ''')
        
        # Tabela de Vínculo Parceiro-Loja
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS parceiro_loja (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                parceiro_id INTEGER,
                loja_id INTEGER,
                FOREIGN KEY (parceiro_id) REFERENCES parceiros(id),
                FOREIGN KEY (loja_id) REFERENCES lojas(id),
                UNIQUE(parceiro_id, loja_id)
            )
        ''')
        
        # Tabela de Comprovantes
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS comprovantes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                parceiro_id INTEGER,
                loja_id INTEGER,
                data_entrega DATE,
                qtd_20l INTEGER DEFAULT 0,
                qtd_10l INTEGER DEFAULT 0,
                qtd_cx_copo INTEGER DEFAULT 0,
                qtd_1500ml INTEGER DEFAULT 0,
                assinatura TEXT,
                arquivo_comprovante TEXT,
                data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (parceiro_id) REFERENCES parceiros(id),
                FOREIGN KEY (loja_id) REFERENCES lojas(id)
            )
        ''')
        
        self.conn.commit()
    
    def create_widgets(self):
        """Cria a interface principal"""
        # Frame superior com título
        header_frame = tk.Frame(self.root, bg='#2c3e50', height=60)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="Sistema de Gerenciamento de Entregas", 
                              font=('Arial', 18, 'bold'), bg='#2c3e50', fg='white')
        title_label.pack(pady=15)
        
        # Frame principal com notebook (abas)
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Notebook para as abas
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True)
        
        # Criar abas
        self.create_dashboard_tab()
        self.create_marcas_tab()
        self.create_lojas_tab()
        self.create_parceiros_tab()
        self.create_comprovantes_tab()
        self.create_relatorios_tab()
    
    def create_dashboard_tab(self):
        """Cria a aba de Dashboard"""
        dashboard_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(dashboard_frame, text='📊 Dashboard')
        
        # Título
        title = tk.Label(dashboard_frame, text="Dashboard - Visão Geral", 
                        font=('Arial', 16, 'bold'), bg='white')
        title.pack(pady=20)
        
        # Frame para os cards
        cards_frame = tk.Frame(dashboard_frame, bg='white')
        cards_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Card - Parceiros que enviaram
        card1 = tk.Frame(cards_frame, bg='#3498db', relief='raised', borderwidth=2)
        card1.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
        
        tk.Label(card1, text="Parceiros com Entregas", font=('Arial', 12, 'bold'), 
                bg='#3498db', fg='white').pack(pady=10)
        self.lbl_parceiros_enviaram = tk.Label(card1, text="0 / 0", 
                                              font=('Arial', 24, 'bold'), 
                                              bg='#3498db', fg='white')
        self.lbl_parceiros_enviaram.pack(pady=10)
        
        # Card - Percentual de relatórios
        card2 = tk.Frame(cards_frame, bg='#2ecc71', relief='raised', borderwidth=2)
        card2.grid(row=0, column=1, padx=10, pady=10, sticky='nsew')
        
        tk.Label(card2, text="Relatórios Preenchidos", font=('Arial', 12, 'bold'), 
                bg='#2ecc71', fg='white').pack(pady=10)
        self.lbl_percentual_relatorios = tk.Label(card2, text="0%", 
                                                 font=('Arial', 24, 'bold'), 
                                                 bg='#2ecc71', fg='white')
        self.lbl_percentual_relatorios.pack(pady=10)
        
        # Card - Total de Lojas
        card3 = tk.Frame(cards_frame, bg='#e74c3c', relief='raised', borderwidth=2)
        card3.grid(row=0, column=2, padx=10, pady=10, sticky='nsew')
        
        tk.Label(card3, text="Total de Lojas", font=('Arial', 12, 'bold'), 
                bg='#e74c3c', fg='white').pack(pady=10)
        self.lbl_total_lojas = tk.Label(card3, text="0", 
                                       font=('Arial', 24, 'bold'), 
                                       bg='#e74c3c', fg='white')
        self.lbl_total_lojas.pack(pady=10)
        
        # Configurar grid
        cards_frame.grid_columnconfigure(0, weight=1)
        cards_frame.grid_columnconfigure(1, weight=1)
        cards_frame.grid_columnconfigure(2, weight=1)
        
        # Frame para lista de parceiros
        list_frame = tk.LabelFrame(dashboard_frame, text="Farol de Parceiros", 
                                  font=('Arial', 12, 'bold'), bg='white')
        list_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Treeview para parceiros
        columns = ('Parceiro', 'Status', 'Última Entrega')
        self.tree_dashboard = ttk.Treeview(list_frame, columns=columns, show='headings', height=10)
        
        self.tree_dashboard.heading('Parceiro', text='Parceiro')
        self.tree_dashboard.heading('Status', text='Status')
        self.tree_dashboard.heading('Última Entrega', text='Última Entrega')
        
        self.tree_dashboard.column('Parceiro', width=300)
        self.tree_dashboard.column('Status', width=150)
        self.tree_dashboard.column('Última Entrega', width=150)
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.tree_dashboard.yview)
        self.tree_dashboard.configure(yscrollcommand=scrollbar.set)
        
        self.tree_dashboard.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Botão atualizar
        btn_frame = tk.Frame(dashboard_frame, bg='white')
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="🔄 Atualizar Dashboard", font=('Arial', 11),
                 bg='#3498db', fg='white', command=self.atualizar_dashboard,
                 padx=20, pady=10).pack()
        
        # Atualizar dashboard ao criar
        self.atualizar_dashboard()
    
    def create_marcas_tab(self):
        """Cria a aba de Marcas"""
        marcas_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(marcas_frame, text='🏢 Marcas')
        
        # Frame de cadastro
        cadastro_frame = tk.LabelFrame(marcas_frame, text="Cadastro de Marca", 
                                      font=('Arial', 11, 'bold'), bg='white')
        cadastro_frame.pack(fill='x', padx=20, pady=10)
        
        # Campos
        tk.Label(cadastro_frame, text="Nome da Marca:", bg='white').grid(row=0, column=0, padx=10, pady=5, sticky='w')
        self.entry_marca_nome = tk.Entry(cadastro_frame, width=40)
        self.entry_marca_nome.grid(row=0, column=1, padx=10, pady=5)
        
        tk.Label(cadastro_frame, text="Código Disagua:", bg='white').grid(row=1, column=0, padx=10, pady=5, sticky='w')
        self.entry_marca_codigo = tk.Entry(cadastro_frame, width=40)
        self.entry_marca_codigo.grid(row=1, column=1, padx=10, pady=5)
        
        # Botões
        btn_frame = tk.Frame(cadastro_frame, bg='white')
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        tk.Button(btn_frame, text="Salvar Marca", bg='#2ecc71', fg='white',
                 command=self.salvar_marca, padx=20, pady=5).pack(side='left', padx=5)
        tk.Button(btn_frame, text="Limpar", bg='#95a5a6', fg='white',
                 command=self.limpar_marca, padx=20, pady=5).pack(side='left', padx=5)
        
        # Frame de listagem
        list_frame = tk.LabelFrame(marcas_frame, text="Marcas Cadastradas", 
                                  font=('Arial', 11, 'bold'), bg='white')
        list_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Treeview
        columns = ('ID', 'Nome', 'Código Disagua')
        self.tree_marcas = ttk.Treeview(list_frame, columns=columns, show='headings', height=12)
        
        for col in columns:
            self.tree_marcas.heading(col, text=col)
            self.tree_marcas.column(col, width=200)
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.tree_marcas.yview)
        self.tree_marcas.configure(yscrollcommand=scrollbar.set)
        
        self.tree_marcas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Botões de ação
        action_frame = tk.Frame(marcas_frame, bg='white')
        action_frame.pack(pady=10)
        
        tk.Button(action_frame, text="Editar", bg='#3498db', fg='white',
                 command=self.editar_marca, padx=15, pady=5).pack(side='left', padx=5)
        tk.Button(action_frame, text="Excluir", bg='#e74c3c', fg='white',
                 command=self.excluir_marca, padx=15, pady=5).pack(side='left', padx=5)
        tk.Button(action_frame, text="Atualizar Lista", bg='#95a5a6', fg='white',
                 command=self.carregar_marcas, padx=15, pady=5).pack(side='left', padx=5)
        
        self.carregar_marcas()
    
    def create_lojas_tab(self):
        """Cria a aba de Lojas"""
        lojas_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(lojas_frame, text='🏪 Lojas')
        
        # Frame de cadastro com scroll
        canvas = tk.Canvas(lojas_frame, bg='white')
        scrollbar = ttk.Scrollbar(lojas_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Frame de cadastro
        cadastro_frame = tk.LabelFrame(scrollable_frame, text="Cadastro de Loja", 
                                      font=('Arial', 11, 'bold'), bg='white')
        cadastro_frame.pack(fill='x', padx=20, pady=10)
        
        # Campos - Coluna 1
        tk.Label(cadastro_frame, text="Marca:", bg='white').grid(row=0, column=0, padx=10, pady=5, sticky='w')
        self.combo_loja_marca = ttk.Combobox(cadastro_frame, width=37, state='readonly')
        self.combo_loja_marca.grid(row=0, column=1, padx=10, pady=5)
        
        tk.Label(cadastro_frame, text="Nome da Loja:", bg='white').grid(row=1, column=0, padx=10, pady=5, sticky='w')
        self.entry_loja_nome = tk.Entry(cadastro_frame, width=40)
        self.entry_loja_nome.grid(row=1, column=1, padx=10, pady=5)
        
        tk.Label(cadastro_frame, text="Código Disagua:", bg='white').grid(row=2, column=0, padx=10, pady=5, sticky='w')
        self.entry_loja_codigo = tk.Entry(cadastro_frame, width=40)
        self.entry_loja_codigo.grid(row=2, column=1, padx=10, pady=5)
        
        tk.Label(cadastro_frame, text="Local de Entrega:", bg='white').grid(row=3, column=0, padx=10, pady=5, sticky='w')
        self.entry_loja_local = tk.Entry(cadastro_frame, width=40)
        self.entry_loja_local.grid(row=3, column=1, padx=10, pady=5)
        
        tk.Label(cadastro_frame, text="Município:", bg='white').grid(row=4, column=0, padx=10, pady=5, sticky='w')
        self.entry_loja_municipio = tk.Entry(cadastro_frame, width=40)
        self.entry_loja_municipio.grid(row=4, column=1, padx=10, pady=5)
        
        tk.Label(cadastro_frame, text="Estado:", bg='white').grid(row=5, column=0, padx=10, pady=5, sticky='w')
        self.entry_loja_estado = tk.Entry(cadastro_frame, width=40)
        self.entry_loja_estado.grid(row=5, column=1, padx=10, pady=5)
        
        # Coluna 2 - Preços
        tk.Label(cadastro_frame, text="Valor 20L (R$):", bg='white').grid(row=0, column=2, padx=10, pady=5, sticky='w')
        self.entry_loja_valor_20l = tk.Entry(cadastro_frame, width=20)
        self.entry_loja_valor_20l.grid(row=0, column=3, padx=10, pady=5)
        
        tk.Label(cadastro_frame, text="Valor 10L (R$):", bg='white').grid(row=1, column=2, padx=10, pady=5, sticky='w')
        self.entry_loja_valor_10l = tk.Entry(cadastro_frame, width=20)
        self.entry_loja_valor_10l.grid(row=1, column=3, padx=10, pady=5)
        
        tk.Label(cadastro_frame, text="Valor Cx Copo (R$):", bg='white').grid(row=2, column=2, padx=10, pady=5, sticky='w')
        self.entry_loja_valor_cx_copo = tk.Entry(cadastro_frame, width=20)
        self.entry_loja_valor_cx_copo.grid(row=2, column=3, padx=10, pady=5)
        
        tk.Label(cadastro_frame, text="Valor 1500ml (R$):", bg='white').grid(row=3, column=2, padx=10, pady=5, sticky='w')
        self.entry_loja_valor_1500ml = tk.Entry(cadastro_frame, width=20)
        self.entry_loja_valor_1500ml.grid(row=3, column=3, padx=10, pady=5)
        
        # Botões
        btn_frame = tk.Frame(cadastro_frame, bg='white')
        btn_frame.grid(row=6, column=0, columnspan=4, pady=10)
        
        tk.Button(btn_frame, text="Salvar Loja", bg='#2ecc71', fg='white',
                 command=self.salvar_loja, padx=20, pady=5).pack(side='left', padx=5)
        tk.Button(btn_frame, text="Limpar", bg='#95a5a6', fg='white',
                 command=self.limpar_loja, padx=20, pady=5).pack(side='left', padx=5)
        
        # Frame de listagem
        list_frame = tk.LabelFrame(scrollable_frame, text="Lojas Cadastradas", 
                                  font=('Arial', 11, 'bold'), bg='white')
        list_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Treeview
        columns = ('ID', 'Marca', 'Nome', 'Município', 'Estado', 'Valor 20L')
        self.tree_lojas = ttk.Treeview(list_frame, columns=columns, show='headings', height=10)
        
        for col in columns:
            self.tree_lojas.heading(col, text=col)
        
        self.tree_lojas.column('ID', width=50)
        self.tree_lojas.column('Marca', width=150)
        self.tree_lojas.column('Nome', width=200)
        self.tree_lojas.column('Município', width=150)
        self.tree_lojas.column('Estado', width=80)
        self.tree_lojas.column('Valor 20L', width=100)
        
        scrollbar_tree = ttk.Scrollbar(list_frame, orient='vertical', command=self.tree_lojas.yview)
        self.tree_lojas.configure(yscrollcommand=scrollbar_tree.set)
        
        self.tree_lojas.pack(side='left', fill='both', expand=True)
        scrollbar_tree.pack(side='right', fill='y')
        
        # Botões de ação
        action_frame = tk.Frame(scrollable_frame, bg='white')
        action_frame.pack(pady=10)
        
        tk.Button(action_frame, text="Editar", bg='#3498db', fg='white',
                 command=self.editar_loja, padx=15, pady=5).pack(side='left', padx=5)
        tk.Button(action_frame, text="Excluir", bg='#e74c3c', fg='white',
                 command=self.excluir_loja, padx=15, pady=5).pack(side='left', padx=5)
        tk.Button(action_frame, text="Atualizar Lista", bg='#95a5a6', fg='white',
                 command=self.carregar_lojas, padx=15, pady=5).pack(side='left', padx=5)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.carregar_lojas()
        self.atualizar_combo_marcas()
    
    def create_parceiros_tab(self):
        """Cria a aba de Parceiros"""
        parceiros_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(parceiros_frame, text='🚚 Parceiros')
        
        # Notebook interno para Cadastro e Lojas do Parceiro
        parceiro_notebook = ttk.Notebook(parceiros_frame)
        parceiro_notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Aba de Cadastro
        cadastro_tab = tk.Frame(parceiro_notebook, bg='white')
        parceiro_notebook.add(cadastro_tab, text='Cadastro de Parceiro')
        
        # Canvas para scroll
        canvas = tk.Canvas(cadastro_tab, bg='white')
        scrollbar = ttk.Scrollbar(cadastro_tab, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Frame de cadastro
        cadastro_frame = tk.LabelFrame(scrollable_frame, text="Dados do Parceiro", 
                                      font=('Arial', 11, 'bold'), bg='white')
        cadastro_frame.pack(fill='x', padx=20, pady=10)
        
        # Linha 1
        tk.Label(cadastro_frame, text="Nome do Parceiro:", bg='white').grid(row=0, column=0, padx=10, pady=5, sticky='w')
        self.entry_parceiro_nome = tk.Entry(cadastro_frame, width=30)
        self.entry_parceiro_nome.grid(row=0, column=1, padx=10, pady=5)
        
        tk.Label(cadastro_frame, text="Distribuidora:", bg='white').grid(row=0, column=2, padx=10, pady=5, sticky='w')
        self.entry_parceiro_distrib = tk.Entry(cadastro_frame, width=30)
        self.entry_parceiro_distrib.grid(row=0, column=3, padx=10, pady=5)
        
        # Linha 2
        tk.Label(cadastro_frame, text="Cidade:", bg='white').grid(row=1, column=0, padx=10, pady=5, sticky='w')
        self.entry_parceiro_cidade = tk.Entry(cadastro_frame, width=30)
        self.entry_parceiro_cidade.grid(row=1, column=1, padx=10, pady=5)
        
        tk.Label(cadastro_frame, text="Estado:", bg='white').grid(row=1, column=2, padx=10, pady=5, sticky='w')
        self.entry_parceiro_estado = tk.Entry(cadastro_frame, width=30)
        self.entry_parceiro_estado.grid(row=1, column=3, padx=10, pady=5)
        
        # Linha 3
        tk.Label(cadastro_frame, text="CNPJ:", bg='white').grid(row=2, column=0, padx=10, pady=5, sticky='w')
        self.entry_parceiro_cnpj = tk.Entry(cadastro_frame, width=30)
        self.entry_parceiro_cnpj.grid(row=2, column=1, padx=10, pady=5)
        
        tk.Label(cadastro_frame, text="Telefone:", bg='white').grid(row=2, column=2, padx=10, pady=5, sticky='w')
        self.entry_parceiro_telefone = tk.Entry(cadastro_frame, width=30)
        self.entry_parceiro_telefone.grid(row=2, column=3, padx=10, pady=5)
        
        # Linha 4
        tk.Label(cadastro_frame, text="Email:", bg='white').grid(row=3, column=0, padx=10, pady=5, sticky='w')
        self.entry_parceiro_email = tk.Entry(cadastro_frame, width=30)
        self.entry_parceiro_email.grid(row=3, column=1, padx=10, pady=5)
        
        tk.Label(cadastro_frame, text="Dia do Pagamento:", bg='white').grid(row=3, column=2, padx=10, pady=5, sticky='w')
        self.entry_parceiro_dia_pgto = tk.Entry(cadastro_frame, width=30)
        self.entry_parceiro_dia_pgto.grid(row=3, column=3, padx=10, pady=5)
        
        # Linha 5 - Dados bancários
        tk.Label(cadastro_frame, text="Banco:", bg='white').grid(row=4, column=0, padx=10, pady=5, sticky='w')
        self.entry_parceiro_banco = tk.Entry(cadastro_frame, width=30)
        self.entry_parceiro_banco.grid(row=4, column=1, padx=10, pady=5)
        
        tk.Label(cadastro_frame, text="Agência:", bg='white').grid(row=4, column=2, padx=10, pady=5, sticky='w')
        self.entry_parceiro_agencia = tk.Entry(cadastro_frame, width=30)
        self.entry_parceiro_agencia.grid(row=4, column=3, padx=10, pady=5)
        
        # Linha 6
        tk.Label(cadastro_frame, text="Conta:", bg='white').grid(row=5, column=0, padx=10, pady=5, sticky='w')
        self.entry_parceiro_conta = tk.Entry(cadastro_frame, width=30)
        self.entry_parceiro_conta.grid(row=5, column=1, padx=10, pady=5)
        
        tk.Label(cadastro_frame, text="Chave PIX:", bg='white').grid(row=5, column=2, padx=10, pady=5, sticky='w')
        self.entry_parceiro_pix = tk.Entry(cadastro_frame, width=30)
        self.entry_parceiro_pix.grid(row=5, column=3, padx=10, pady=5)
        
        # Frame de valores
        valores_frame = tk.LabelFrame(scrollable_frame, text="Valores do Parceiro (Pagamento)", 
                                     font=('Arial', 11, 'bold'), bg='white')
        valores_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(valores_frame, text="Valor 20L (R$):", bg='white').grid(row=0, column=0, padx=10, pady=5, sticky='w')
        self.entry_parceiro_valor_20l = tk.Entry(valores_frame, width=20)
        self.entry_parceiro_valor_20l.grid(row=0, column=1, padx=10, pady=5)
        
        tk.Label(valores_frame, text="Valor 10L (R$):", bg='white').grid(row=0, column=2, padx=10, pady=5, sticky='w')
        self.entry_parceiro_valor_10l = tk.Entry(valores_frame, width=20)
        self.entry_parceiro_valor_10l.grid(row=0, column=3, padx=10, pady=5)
        
        tk.Label(valores_frame, text="Valor Cx Copo (R$):", bg='white').grid(row=1, column=0, padx=10, pady=5, sticky='w')
        self.entry_parceiro_valor_cx_copo = tk.Entry(valores_frame, width=20)
        self.entry_parceiro_valor_cx_copo.grid(row=1, column=1, padx=10, pady=5)
        
        tk.Label(valores_frame, text="Valor 1500ml (R$):", bg='white').grid(row=1, column=2, padx=10, pady=5, sticky='w')
        self.entry_parceiro_valor_1500ml = tk.Entry(valores_frame, width=20)
        self.entry_parceiro_valor_1500ml.grid(row=1, column=3, padx=10, pady=5)
        
        # Botões
        btn_frame = tk.Frame(scrollable_frame, bg='white')
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="Salvar Parceiro", bg='#2ecc71', fg='white',
                 command=self.salvar_parceiro, padx=20, pady=5).pack(side='left', padx=5)
        tk.Button(btn_frame, text="Limpar", bg='#95a5a6', fg='white',
                 command=self.limpar_parceiro, padx=20, pady=5).pack(side='left', padx=5)
        
        # Frame de listagem
        list_frame = tk.LabelFrame(scrollable_frame, text="Parceiros Cadastrados", 
                                  font=('Arial', 11, 'bold'), bg='white')
        list_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        columns = ('ID', 'Nome', 'Cidade', 'Estado', 'CNPJ', 'Telefone')
        self.tree_parceiros = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)
        
        for col in columns:
            self.tree_parceiros.heading(col, text=col)
        
        self.tree_parceiros.column('ID', width=50)
        self.tree_parceiros.column('Nome', width=200)
        self.tree_parceiros.column('Cidade', width=150)
        self.tree_parceiros.column('Estado', width=80)
        self.tree_parceiros.column('CNPJ', width=150)
        self.tree_parceiros.column('Telefone', width=120)
        
        scrollbar_tree = ttk.Scrollbar(list_frame, orient='vertical', command=self.tree_parceiros.yview)
        self.tree_parceiros.configure(yscrollcommand=scrollbar_tree.set)
        
        self.tree_parceiros.pack(side='left', fill='both', expand=True)
        scrollbar_tree.pack(side='right', fill='y')
        
        # Botões de ação
        action_frame = tk.Frame(scrollable_frame, bg='white')
        action_frame.pack(pady=10)
        
        tk.Button(action_frame, text="Editar", bg='#3498db', fg='white',
                 command=self.editar_parceiro, padx=15, pady=5).pack(side='left', padx=5)
        tk.Button(action_frame, text="Excluir", bg='#e74c3c', fg='white',
                 command=self.excluir_parceiro, padx=15, pady=5).pack(side='left', padx=5)
        tk.Button(action_frame, text="Atualizar Lista", bg='#95a5a6', fg='white',
                 command=self.carregar_parceiros, padx=15, pady=5).pack(side='left', padx=5)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Aba de Lojas do Parceiro
        self.create_lojas_parceiro_tab(parceiro_notebook)
        
        self.carregar_parceiros()
    
    def create_lojas_parceiro_tab(self, parent_notebook):
        """Cria a aba de vinculação de lojas ao parceiro"""
        lojas_tab = tk.Frame(parent_notebook, bg='white')
        parent_notebook.add(lojas_tab, text='Lojas do Parceiro')
        
        # Seleção de parceiro
        sel_frame = tk.LabelFrame(lojas_tab, text="Selecione o Parceiro", 
                                 font=('Arial', 11, 'bold'), bg='white')
        sel_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(sel_frame, text="Parceiro:", bg='white').pack(side='left', padx=10, pady=10)
        self.combo_vincular_parceiro = ttk.Combobox(sel_frame, width=50, state='readonly')
        self.combo_vincular_parceiro.pack(side='left', padx=10, pady=10)
        self.combo_vincular_parceiro.bind('<<ComboboxSelected>>', self.carregar_lojas_vinculacao)
        
        # Frame dividido
        main_frame = tk.Frame(lojas_tab, bg='white')
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Lojas disponíveis
        disponiveis_frame = tk.LabelFrame(main_frame, text="Lojas Disponíveis", 
                                         font=('Arial', 10, 'bold'), bg='white')
        disponiveis_frame.pack(side='left', fill='both', expand=True, padx=5)
        
        self.tree_lojas_disponiveis = ttk.Treeview(disponiveis_frame, 
                                                  columns=('ID', 'Nome', 'Cidade', 'Estado'),
                                                  show='headings', height=15)
        
        self.tree_lojas_disponiveis.heading('ID', text='ID')
        self.tree_lojas_disponiveis.heading('Nome', text='Nome')
        self.tree_lojas_disponiveis.heading('Cidade', text='Cidade')
        self.tree_lojas_disponiveis.heading('Estado', text='Estado')
        
        self.tree_lojas_disponiveis.column('ID', width=50)
        self.tree_lojas_disponiveis.column('Nome', width=200)
        self.tree_lojas_disponiveis.column('Cidade', width=120)
        self.tree_lojas_disponiveis.column('Estado', width=60)
        
        scrollbar1 = ttk.Scrollbar(disponiveis_frame, orient='vertical', 
                                  command=self.tree_lojas_disponiveis.yview)
        self.tree_lojas_disponiveis.configure(yscrollcommand=scrollbar1.set)
        
        self.tree_lojas_disponiveis.pack(side='left', fill='both', expand=True)
        scrollbar1.pack(side='right', fill='y')
        
        # Botões de ação
        btn_frame = tk.Frame(main_frame, bg='white')
        btn_frame.pack(side='left', padx=10)
        
        tk.Button(btn_frame, text="➡️\nAdicionar", bg='#2ecc71', fg='white',
                 command=self.vincular_loja, padx=10, pady=20).pack(pady=10)
        tk.Button(btn_frame, text="⬅️\nRemover", bg='#e74c3c', fg='white',
                 command=self.desvincular_loja, padx=10, pady=20).pack(pady=10)
        
        # Lojas vinculadas
        vinculadas_frame = tk.LabelFrame(main_frame, text="Lojas Vinculadas", 
                                        font=('Arial', 10, 'bold'), bg='white')
        vinculadas_frame.pack(side='left', fill='both', expand=True, padx=5)
        
        self.tree_lojas_vinculadas = ttk.Treeview(vinculadas_frame,
                                                 columns=('ID', 'Nome', 'Cidade', 'Estado'),
                                                 show='headings', height=15)
        
        self.tree_lojas_vinculadas.heading('ID', text='ID')
        self.tree_lojas_vinculadas.heading('Nome', text='Nome')
        self.tree_lojas_vinculadas.heading('Cidade', text='Cidade')
        self.tree_lojas_vinculadas.heading('Estado', text='Estado')
        
        self.tree_lojas_vinculadas.column('ID', width=50)
        self.tree_lojas_vinculadas.column('Nome', width=200)
        self.tree_lojas_vinculadas.column('Cidade', width=120)
        self.tree_lojas_vinculadas.column('Estado', width=60)
        
        scrollbar2 = ttk.Scrollbar(vinculadas_frame, orient='vertical',
                                  command=self.tree_lojas_vinculadas.yview)
        self.tree_lojas_vinculadas.configure(yscrollcommand=scrollbar2.set)
        
        self.tree_lojas_vinculadas.pack(side='left', fill='both', expand=True)
        scrollbar2.pack(side='right', fill='y')
        
        self.atualizar_combo_parceiros_vinculacao()
    
    def create_comprovantes_tab(self):
        """Cria a aba de Comprovantes"""
        comprovantes_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(comprovantes_frame, text='📋 Comprovantes')
        
        # Frame de cadastro
        cadastro_frame = tk.LabelFrame(comprovantes_frame, text="Registrar Comprovante de Entrega", 
                                      font=('Arial', 11, 'bold'), bg='white')
        cadastro_frame.pack(fill='x', padx=20, pady=10)
        
        # Linha 1
        tk.Label(cadastro_frame, text="Parceiro:", bg='white').grid(row=0, column=0, padx=10, pady=5, sticky='w')
        self.combo_comprov_parceiro = ttk.Combobox(cadastro_frame, width=35, state='readonly')
        self.combo_comprov_parceiro.grid(row=0, column=1, padx=10, pady=5)
        self.combo_comprov_parceiro.bind('<<ComboboxSelected>>', self.atualizar_lojas_comprovante)
        
        tk.Label(cadastro_frame, text="Loja:", bg='white').grid(row=0, column=2, padx=10, pady=5, sticky='w')
        self.combo_comprov_loja = ttk.Combobox(cadastro_frame, width=35, state='readonly')
        self.combo_comprov_loja.grid(row=0, column=3, padx=10, pady=5)
        
        # Linha 2
        tk.Label(cadastro_frame, text="Data da Entrega:", bg='white').grid(row=1, column=0, padx=10, pady=5, sticky='w')
        self.entry_comprov_data = tk.Entry(cadastro_frame, width=38)
        self.entry_comprov_data.grid(row=1, column=1, padx=10, pady=5)
        self.entry_comprov_data.insert(0, datetime.now().strftime('%d/%m/%Y'))
        
        tk.Label(cadastro_frame, text="Assinatura:", bg='white').grid(row=1, column=2, padx=10, pady=5, sticky='w')
        self.entry_comprov_assinatura = tk.Entry(cadastro_frame, width=38)
        self.entry_comprov_assinatura.grid(row=1, column=3, padx=10, pady=5)
        
        # Frame de produtos
        produtos_frame = tk.LabelFrame(cadastro_frame, text="Produtos Entregues", bg='white')
        produtos_frame.grid(row=2, column=0, columnspan=4, padx=10, pady=10, sticky='ew')
        
        tk.Label(produtos_frame, text="Qtd 20L:", bg='white').grid(row=0, column=0, padx=10, pady=5, sticky='w')
        self.entry_comprov_qtd_20l = tk.Entry(produtos_frame, width=15)
        self.entry_comprov_qtd_20l.grid(row=0, column=1, padx=10, pady=5)
        self.entry_comprov_qtd_20l.insert(0, '0')
        
        tk.Label(produtos_frame, text="Qtd 10L:", bg='white').grid(row=0, column=2, padx=10, pady=5, sticky='w')
        self.entry_comprov_qtd_10l = tk.Entry(produtos_frame, width=15)
        self.entry_comprov_qtd_10l.grid(row=0, column=3, padx=10, pady=5)
        self.entry_comprov_qtd_10l.insert(0, '0')
        
        tk.Label(produtos_frame, text="Qtd Cx Copo:", bg='white').grid(row=1, column=0, padx=10, pady=5, sticky='w')
        self.entry_comprov_qtd_cx_copo = tk.Entry(produtos_frame, width=15)
        self.entry_comprov_qtd_cx_copo.grid(row=1, column=1, padx=10, pady=5)
        self.entry_comprov_qtd_cx_copo.insert(0, '0')
        
        tk.Label(produtos_frame, text="Qtd 1500ml:", bg='white').grid(row=1, column=2, padx=10, pady=5, sticky='w')
        self.entry_comprov_qtd_1500ml = tk.Entry(produtos_frame, width=15)
        self.entry_comprov_qtd_1500ml.grid(row=1, column=3, padx=10, pady=5)
        self.entry_comprov_qtd_1500ml.insert(0, '0')
        
        # Arquivo
        tk.Label(cadastro_frame, text="Arquivo (opcional):", bg='white').grid(row=3, column=0, padx=10, pady=5, sticky='w')
        self.entry_comprov_arquivo = tk.Entry(cadastro_frame, width=50)
        self.entry_comprov_arquivo.grid(row=3, column=1, columnspan=2, padx=10, pady=5)
        tk.Button(cadastro_frame, text="Selecionar", command=self.selecionar_arquivo_comprovante).grid(row=3, column=3, padx=10, pady=5)
        
        # Botões
        btn_frame = tk.Frame(cadastro_frame, bg='white')
        btn_frame.grid(row=4, column=0, columnspan=4, pady=10)
        
        tk.Button(btn_frame, text="Salvar Comprovante", bg='#2ecc71', fg='white',
                 command=self.salvar_comprovante, padx=20, pady=5).pack(side='left', padx=5)
        tk.Button(btn_frame, text="Limpar", bg='#95a5a6', fg='white',
                 command=self.limpar_comprovante, padx=20, pady=5).pack(side='left', padx=5)
        
        # Frame de listagem
        list_frame = tk.LabelFrame(comprovantes_frame, text="Comprovantes Registrados", 
                                  font=('Arial', 11, 'bold'), bg='white')
        list_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        columns = ('ID', 'Data', 'Parceiro', 'Loja', '20L', '10L', 'Cx Copo', '1500ml')
        self.tree_comprovantes = ttk.Treeview(list_frame, columns=columns, show='headings', height=12)
        
        for col in columns:
            self.tree_comprovantes.heading(col, text=col)
        
        self.tree_comprovantes.column('ID', width=50)
        self.tree_comprovantes.column('Data', width=100)
        self.tree_comprovantes.column('Parceiro', width=150)
        self.tree_comprovantes.column('Loja', width=150)
        self.tree_comprovantes.column('20L', width=80)
        self.tree_comprovantes.column('10L', width=80)
        self.tree_comprovantes.column('Cx Copo', width=80)
        self.tree_comprovantes.column('1500ml', width=80)
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.tree_comprovantes.yview)
        self.tree_comprovantes.configure(yscrollcommand=scrollbar.set)
        
        self.tree_comprovantes.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Botões de ação
        action_frame = tk.Frame(comprovantes_frame, bg='white')
        action_frame.pack(pady=10)
        
        tk.Button(action_frame, text="Excluir", bg='#e74c3c', fg='white',
                 command=self.excluir_comprovante, padx=15, pady=5).pack(side='left', padx=5)
        tk.Button(action_frame, text="Atualizar Lista", bg='#95a5a6', fg='white',
                 command=self.carregar_comprovantes, padx=15, pady=5).pack(side='left', padx=5)
        
        self.carregar_comprovantes()
        self.atualizar_combo_parceiros_comprovante()
    
    def create_relatorios_tab(self):
        """Cria a aba de Relatórios"""
        relatorios_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(relatorios_frame, text='📊 Relatórios')
        
        # Notebook interno
        rel_notebook = ttk.Notebook(relatorios_frame)
        rel_notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Aba de Relatório de Marca
        marca_tab = tk.Frame(rel_notebook, bg='white')
        rel_notebook.add(marca_tab, text='Relatório por Marca')
        
        # Filtros
        filtro_frame = tk.LabelFrame(marca_tab, text="Filtros", font=('Arial', 11, 'bold'), bg='white')
        filtro_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(filtro_frame, text="Marca:", bg='white').grid(row=0, column=0, padx=10, pady=5, sticky='w')
        self.combo_rel_marca = ttk.Combobox(filtro_frame, width=30, state='readonly')
        self.combo_rel_marca.grid(row=0, column=1, padx=10, pady=5)
        
        tk.Label(filtro_frame, text="Data Início:", bg='white').grid(row=0, column=2, padx=10, pady=5, sticky='w')
        self.entry_rel_marca_data_inicio = tk.Entry(filtro_frame, width=15)
        self.entry_rel_marca_data_inicio.grid(row=0, column=3, padx=10, pady=5)
        
        tk.Label(filtro_frame, text="Data Fim:", bg='white').grid(row=0, column=4, padx=10, pady=5, sticky='w')
        self.entry_rel_marca_data_fim = tk.Entry(filtro_frame, width=15)
        self.entry_rel_marca_data_fim.grid(row=0, column=5, padx=10, pady=5)
        
        tk.Button(filtro_frame, text="Gerar Relatório", bg='#3498db', fg='white',
                 command=self.gerar_relatorio_marca, padx=20, pady=5).grid(row=0, column=6, padx=10, pady=5)
        
        # Resultado
        resultado_frame = tk.LabelFrame(marca_tab, text="Resultado", font=('Arial', 11, 'bold'), bg='white')
        resultado_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        columns = ('Loja', 'Local', 'Município', '20L', '10L', 'Cx Copo', '1500ml', 'Total (R$)')
        self.tree_rel_marca = ttk.Treeview(resultado_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.tree_rel_marca.heading(col, text=col)
        
        self.tree_rel_marca.column('Loja', width=150)
        self.tree_rel_marca.column('Local', width=150)
        self.tree_rel_marca.column('Município', width=120)
        self.tree_rel_marca.column('20L', width=60)
        self.tree_rel_marca.column('10L', width=60)
        self.tree_rel_marca.column('Cx Copo', width=80)
        self.tree_rel_marca.column('1500ml', width=80)
        self.tree_rel_marca.column('Total (R$)', width=100)
        
        scrollbar = ttk.Scrollbar(resultado_frame, orient='vertical', command=self.tree_rel_marca.yview)
        self.tree_rel_marca.configure(yscrollcommand=scrollbar.set)
        
        self.tree_rel_marca.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Totalizações
        total_frame = tk.Frame(marca_tab, bg='white')
        total_frame.pack(fill='x', padx=20, pady=10)
        
        self.lbl_total_marca = tk.Label(total_frame, text="Total Geral: R$ 0,00", 
                                       font=('Arial', 12, 'bold'), bg='white')
        self.lbl_total_marca.pack(side='right', padx=10)
        
        tk.Button(total_frame, text="Exportar para Excel", bg='#2ecc71', fg='white',
                 command=lambda: self.exportar_relatorio('marca'), padx=15, pady=5).pack(side='left', padx=5)
        
        # Aba de Relatório de Parceiro
        parceiro_tab = tk.Frame(rel_notebook, bg='white')
        rel_notebook.add(parceiro_tab, text='Relatório por Parceiro')
        
        # Filtros
        filtro_frame2 = tk.LabelFrame(parceiro_tab, text="Filtros", font=('Arial', 11, 'bold'), bg='white')
        filtro_frame2.pack(fill='x', padx=20, pady=10)
        
        tk.Label(filtro_frame2, text="Parceiro:", bg='white').grid(row=0, column=0, padx=10, pady=5, sticky='w')
        self.combo_rel_parceiro = ttk.Combobox(filtro_frame2, width=30, state='readonly')
        self.combo_rel_parceiro.grid(row=0, column=1, padx=10, pady=5)
        
        tk.Label(filtro_frame2, text="Data Início:", bg='white').grid(row=0, column=2, padx=10, pady=5, sticky='w')
        self.entry_rel_parceiro_data_inicio = tk.Entry(filtro_frame2, width=15)
        self.entry_rel_parceiro_data_inicio.grid(row=0, column=3, padx=10, pady=5)
        
        tk.Label(filtro_frame2, text="Data Fim:", bg='white').grid(row=0, column=4, padx=10, pady=5, sticky='w')
        self.entry_rel_parceiro_data_fim = tk.Entry(filtro_frame2, width=15)
        self.entry_rel_parceiro_data_fim.grid(row=0, column=5, padx=10, pady=5)
        
        tk.Button(filtro_frame2, text="Gerar Relatório", bg='#3498db', fg='white',
                 command=self.gerar_relatorio_parceiro, padx=20, pady=5).grid(row=0, column=6, padx=10, pady=5)
        
        # Resultado
        resultado_frame2 = tk.LabelFrame(parceiro_tab, text="Resultado", font=('Arial', 11, 'bold'), bg='white')
        resultado_frame2.pack(fill='both', expand=True, padx=20, pady=10)
        
        columns2 = ('Loja', 'Data', '20L', '10L', 'Cx Copo', '1500ml', 'Total (R$)')
        self.tree_rel_parceiro = ttk.Treeview(resultado_frame2, columns=columns2, show='headings', height=15)
        
        for col in columns2:
            self.tree_rel_parceiro.heading(col, text=col)
        
        self.tree_rel_parceiro.column('Loja', width=200)
        self.tree_rel_parceiro.column('Data', width=100)
        self.tree_rel_parceiro.column('20L', width=80)
        self.tree_rel_parceiro.column('10L', width=80)
        self.tree_rel_parceiro.column('Cx Copo', width=100)
        self.tree_rel_parceiro.column('1500ml', width=100)
        self.tree_rel_parceiro.column('Total (R$)', width=120)
        
        scrollbar2 = ttk.Scrollbar(resultado_frame2, orient='vertical', command=self.tree_rel_parceiro.yview)
        self.tree_rel_parceiro.configure(yscrollcommand=scrollbar2.set)
        
        self.tree_rel_parceiro.pack(side='left', fill='both', expand=True)
        scrollbar2.pack(side='right', fill='y')
        
        # Totalizações
        total_frame2 = tk.Frame(parceiro_tab, bg='white')
        total_frame2.pack(fill='x', padx=20, pady=10)
        
        self.lbl_total_parceiro = tk.Label(total_frame2, text="Total a Receber: R$ 0,00", 
                                          font=('Arial', 12, 'bold'), bg='white')
        self.lbl_total_parceiro.pack(side='right', padx=10)
        
        tk.Button(total_frame2, text="Exportar para Excel", bg='#2ecc71', fg='white',
                 command=lambda: self.exportar_relatorio('parceiro'), padx=15, pady=5).pack(side='left', padx=5)
        
        # Atualizar combos
        self.atualizar_combo_marcas_relatorio()
        self.atualizar_combo_parceiros_relatorio()
    
    # === MÉTODOS DE MARCA ===
    def salvar_marca(self):
        nome = self.entry_marca_nome.get().strip()
        codigo = self.entry_marca_codigo.get().strip()
        
        if not nome or not codigo:
            messagebox.showwarning("Atenção", "Preencha todos os campos!")
            return
        
        try:
            self.cursor.execute("INSERT INTO marcas (nome, codigo_disagua) VALUES (?, ?)", (nome, codigo))
            self.conn.commit()
            messagebox.showinfo("Sucesso", "Marca cadastrada com sucesso!")
            self.limpar_marca()
            self.carregar_marcas()
            self.atualizar_combo_marcas()
        except sqlite3.IntegrityError:
            messagebox.showerror("Erro", "Código Disagua já cadastrado!")
    
    def limpar_marca(self):
        self.entry_marca_nome.delete(0, tk.END)
        self.entry_marca_codigo.delete(0, tk.END)
    
    def carregar_marcas(self):
        for item in self.tree_marcas.get_children():
            self.tree_marcas.delete(item)
        
        self.cursor.execute("SELECT * FROM marcas ORDER BY nome")
        for row in self.cursor.fetchall():
            self.tree_marcas.insert('', 'end', values=row)
    
    def editar_marca(self):
        selected = self.tree_marcas.selection()
        if not selected:
            messagebox.showwarning("Atenção", "Selecione uma marca!")
            return
        
        item = self.tree_marcas.item(selected[0])
        valores = item['values']
        
        self.entry_marca_nome.delete(0, tk.END)
        self.entry_marca_nome.insert(0, valores[1])
        self.entry_marca_codigo.delete(0, tk.END)
        self.entry_marca_codigo.insert(0, valores[2])
        
        # TODO: Implementar atualização
    
    def excluir_marca(self):
        selected = self.tree_marcas.selection()
        if not selected:
            messagebox.showwarning("Atenção", "Selecione uma marca!")
            return
        
        if messagebox.askyesno("Confirmar", "Deseja realmente excluir esta marca?"):
            item = self.tree_marcas.item(selected[0])
            marca_id = item['values'][0]
            
            self.cursor.execute("DELETE FROM marcas WHERE id = ?", (marca_id,))
            self.conn.commit()
            messagebox.showinfo("Sucesso", "Marca excluída!")
            self.carregar_marcas()
            self.atualizar_combo_marcas()
    
    def atualizar_combo_marcas(self):
        self.cursor.execute("SELECT id, nome FROM marcas ORDER BY nome")
        marcas = self.cursor.fetchall()
        self.combo_loja_marca['values'] = [f"{m[0]} - {m[1]}" for m in marcas]
    
    # === MÉTODOS DE LOJA ===
    def salvar_loja(self):
        marca = self.combo_loja_marca.get()
        if not marca:
            messagebox.showwarning("Atenção", "Selecione uma marca!")
            return
        
        marca_id = int(marca.split(' - ')[0])
        nome = self.entry_loja_nome.get().strip()
        codigo = self.entry_loja_codigo.get().strip()
        local = self.entry_loja_local.get().strip()
        municipio = self.entry_loja_municipio.get().strip()
        estado = self.entry_loja_estado.get().strip()
        
        try:
            valor_20l = float(self.entry_loja_valor_20l.get() or 0)
            valor_10l = float(self.entry_loja_valor_10l.get() or 0)
            valor_cx_copo = float(self.entry_loja_valor_cx_copo.get() or 0)
            valor_1500ml = float(self.entry_loja_valor_1500ml.get() or 0)
        except ValueError:
            messagebox.showerror("Erro", "Valores inválidos!")
            return
        
        if not nome or not codigo:
            messagebox.showwarning("Atenção", "Preencha os campos obrigatórios!")
            return
        
        try:
            self.cursor.execute("""
                INSERT INTO lojas (marca_id, nome, codigo_disagua, local_entrega, municipio, estado,
                                  valor_20l, valor_10l, valor_cx_copo, valor_1500ml)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (marca_id, nome, codigo, local, municipio, estado, 
                  valor_20l, valor_10l, valor_cx_copo, valor_1500ml))
            self.conn.commit()
            messagebox.showinfo("Sucesso", "Loja cadastrada com sucesso!")
            self.limpar_loja()
            self.carregar_lojas()
        except sqlite3.IntegrityError:
            messagebox.showerror("Erro", "Código Disagua já cadastrado!")
    
    def limpar_loja(self):
        self.combo_loja_marca.set('')
        self.entry_loja_nome.delete(0, tk.END)
        self.entry_loja_codigo.delete(0, tk.END)
        self.entry_loja_local.delete(0, tk.END)
        self.entry_loja_municipio.delete(0, tk.END)
        self.entry_loja_estado.delete(0, tk.END)
        self.entry_loja_valor_20l.delete(0, tk.END)
        self.entry_loja_valor_10l.delete(0, tk.END)
        self.entry_loja_valor_cx_copo.delete(0, tk.END)
        self.entry_loja_valor_1500ml.delete(0, tk.END)
    
    def carregar_lojas(self):
        for item in self.tree_lojas.get_children():
            self.tree_lojas.delete(item)
        
        self.cursor.execute("""
            SELECT l.id, m.nome, l.nome, l.municipio, l.estado, l.valor_20l
            FROM lojas l
            JOIN marcas m ON l.marca_id = m.id
            ORDER BY l.nome
        """)
        for row in self.cursor.fetchall():
            self.tree_lojas.insert('', 'end', values=row)
    
    def editar_loja(self):
        messagebox.showinfo("Info", "Função de edição será implementada")
    
    def excluir_loja(self):
        selected = self.tree_lojas.selection()
        if not selected:
            messagebox.showwarning("Atenção", "Selecione uma loja!")
            return
        
        if messagebox.askyesno("Confirmar", "Deseja realmente excluir esta loja?"):
            item = self.tree_lojas.item(selected[0])
            loja_id = item['values'][0]
            
            self.cursor.execute("DELETE FROM lojas WHERE id = ?", (loja_id,))
            self.conn.commit()
            messagebox.showinfo("Sucesso", "Loja excluída!")
            self.carregar_lojas()
    
    # === MÉTODOS DE PARCEIRO ===
    def salvar_parceiro(self):
        nome = self.entry_parceiro_nome.get().strip()
        if not nome:
            messagebox.showwarning("Atenção", "Preencha o nome do parceiro!")
            return
        
        try:
            valor_20l = float(self.entry_parceiro_valor_20l.get() or 0)
            valor_10l = float(self.entry_parceiro_valor_10l.get() or 0)
            valor_cx_copo = float(self.entry_parceiro_valor_cx_copo.get() or 0)
            valor_1500ml = float(self.entry_parceiro_valor_1500ml.get() or 0)
            dia_pgto = int(self.entry_parceiro_dia_pgto.get() or 0)
        except ValueError:
            messagebox.showerror("Erro", "Valores inválidos!")
            return
        
        self.cursor.execute("""
            INSERT INTO parceiros (cidade, estado, nome_parceiro, distribuidora, cnpj, telefone,
                                  email, dia_pagamento, banco, agencia, conta, chave_pix,
                                  valor_20l, valor_10l, valor_cx_copo, valor_1500ml)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            self.entry_parceiro_cidade.get(),
            self.entry_parceiro_estado.get(),
            nome,
            self.entry_parceiro_distrib.get(),
            self.entry_parceiro_cnpj.get(),
            self.entry_parceiro_telefone.get(),
            self.entry_parceiro_email.get(),
            dia_pgto,
            self.entry_parceiro_banco.get(),
            self.entry_parceiro_agencia.get(),
            self.entry_parceiro_conta.get(),
            self.entry_parceiro_pix.get(),
            valor_20l, valor_10l, valor_cx_copo, valor_1500ml
        ))
        self.conn.commit()
        messagebox.showinfo("Sucesso", "Parceiro cadastrado com sucesso!")
        self.limpar_parceiro()
        self.carregar_parceiros()
        self.atualizar_combo_parceiros_vinculacao()
        self.atualizar_combo_parceiros_comprovante()
    
    def limpar_parceiro(self):
        self.entry_parceiro_nome.delete(0, tk.END)
        self.entry_parceiro_distrib.delete(0, tk.END)
        self.entry_parceiro_cidade.delete(0, tk.END)
        self.entry_parceiro_estado.delete(0, tk.END)
        self.entry_parceiro_cnpj.delete(0, tk.END)
        self.entry_parceiro_telefone.delete(0, tk.END)
        self.entry_parceiro_email.delete(0, tk.END)
        self.entry_parceiro_dia_pgto.delete(0, tk.END)
        self.entry_parceiro_banco.delete(0, tk.END)
        self.entry_parceiro_agencia.delete(0, tk.END)
        self.entry_parceiro_conta.delete(0, tk.END)
        self.entry_parceiro_pix.delete(0, tk.END)
        self.entry_parceiro_valor_20l.delete(0, tk.END)
        self.entry_parceiro_valor_10l.delete(0, tk.END)
        self.entry_parceiro_valor_cx_copo.delete(0, tk.END)
        self.entry_parceiro_valor_1500ml.delete(0, tk.END)
    
    def carregar_parceiros(self):
        for item in self.tree_parceiros.get_children():
            self.tree_parceiros.delete(item)
        
        self.cursor.execute("SELECT id, nome_parceiro, cidade, estado, cnpj, telefone FROM parceiros ORDER BY nome_parceiro")
        for row in self.cursor.fetchall():
            self.tree_parceiros.insert('', 'end', values=row)
    
    def editar_parceiro(self):
        messagebox.showinfo("Info", "Função de edição será implementada")
    
    def excluir_parceiro(self):
        selected = self.tree_parceiros.selection()
        if not selected:
            messagebox.showwarning("Atenção", "Selecione um parceiro!")
            return
        
        if messagebox.askyesno("Confirmar", "Deseja realmente excluir este parceiro?"):
            item = self.tree_parceiros.item(selected[0])
            parceiro_id = item['values'][0]
            
            self.cursor.execute("DELETE FROM parceiros WHERE id = ?", (parceiro_id,))
            self.conn.commit()
            messagebox.showinfo("Sucesso", "Parceiro excluído!")
            self.carregar_parceiros()
    
    # === MÉTODOS DE VINCULAÇÃO ===
    def atualizar_combo_parceiros_vinculacao(self):
        self.cursor.execute("SELECT id, nome_parceiro FROM parceiros ORDER BY nome_parceiro")
        parceiros = self.cursor.fetchall()
        self.combo_vincular_parceiro['values'] = [f"{p[0]} - {p[1]}" for p in parceiros]
    
    def carregar_lojas_vinculacao(self, event=None):
        parceiro = self.combo_vincular_parceiro.get()
        if not parceiro:
            return
        
        parceiro_id = int(parceiro.split(' - ')[0])
        
        # Limpar árvores
        for item in self.tree_lojas_disponiveis.get_children():
            self.tree_lojas_disponiveis.delete(item)
        for item in self.tree_lojas_vinculadas.get_children():
            self.tree_lojas_vinculadas.delete(item)
        
        # Carregar lojas vinculadas
        self.cursor.execute("""
            SELECT l.id, l.nome, l.municipio, l.estado
            FROM lojas l
            JOIN parceiro_loja pl ON l.id = pl.loja_id
            WHERE pl.parceiro_id = ?
        """, (parceiro_id,))
        
        for row in self.cursor.fetchall():
            self.tree_lojas_vinculadas.insert('', 'end', values=row)
        
        # Carregar lojas disponíveis
        self.cursor.execute("""
            SELECT l.id, l.nome, l.municipio, l.estado
            FROM lojas l
            WHERE l.id NOT IN (
                SELECT loja_id FROM parceiro_loja WHERE parceiro_id = ?
            )
        """, (parceiro_id,))
        
        for row in self.cursor.fetchall():
            self.tree_lojas_disponiveis.insert('', 'end', values=row)
    
    def vincular_loja(self):
        parceiro = self.combo_vincular_parceiro.get()
        if not parceiro:
            messagebox.showwarning("Atenção", "Selecione um parceiro!")
            return
        
        selected = self.tree_lojas_disponiveis.selection()
        if not selected:
            messagebox.showwarning("Atenção", "Selecione uma loja!")
            return
        
        parceiro_id = int(parceiro.split(' - ')[0])
        item = self.tree_lojas_disponiveis.item(selected[0])
        loja_id = item['values'][0]
        
        try:
            self.cursor.execute("INSERT INTO parceiro_loja (parceiro_id, loja_id) VALUES (?, ?)",
                              (parceiro_id, loja_id))
            self.conn.commit()
            self.carregar_lojas_vinculacao()
            messagebox.showinfo("Sucesso", "Loja vinculada!")
        except sqlite3.IntegrityError:
            messagebox.showwarning("Atenção", "Loja já vinculada!")
    
    def desvincular_loja(self):
        parceiro = self.combo_vincular_parceiro.get()
        if not parceiro:
            return
        
        selected = self.tree_lojas_vinculadas.selection()
        if not selected:
            messagebox.showwarning("Atenção", "Selecione uma loja!")
            return
        
        parceiro_id = int(parceiro.split(' - ')[0])
        item = self.tree_lojas_vinculadas.item(selected[0])
        loja_id = item['values'][0]
        
        self.cursor.execute("DELETE FROM parceiro_loja WHERE parceiro_id = ? AND loja_id = ?",
                          (parceiro_id, loja_id))
        self.conn.commit()
        self.carregar_lojas_vinculacao()
        messagebox.showinfo("Sucesso", "Loja desvinculada!")
    
    # === MÉTODOS DE COMPROVANTE ===
    def atualizar_combo_parceiros_comprovante(self):
        self.cursor.execute("SELECT id, nome_parceiro FROM parceiros ORDER BY nome_parceiro")
        parceiros = self.cursor.fetchall()
        self.combo_comprov_parceiro['values'] = [f"{p[0]} - {p[1]}" for p in parceiros]
    
    def atualizar_lojas_comprovante(self, event=None):
        parceiro = self.combo_comprov_parceiro.get()
        if not parceiro:
            return
        
        parceiro_id = int(parceiro.split(' - ')[0])
        
        self.cursor.execute("""
            SELECT l.id, l.nome
            FROM lojas l
            JOIN parceiro_loja pl ON l.id = pl.loja_id
            WHERE pl.parceiro_id = ?
        """, (parceiro_id,))
        
        lojas = self.cursor.fetchall()
        self.combo_comprov_loja['values'] = [f"{l[0]} - {l[1]}" for l in lojas]
    
    def selecionar_arquivo_comprovante(self):
        filename = filedialog.askopenfilename(
            title="Selecionar Comprovante",
            filetypes=[("Imagens", "*.png *.jpg *.jpeg"), ("PDF", "*.pdf"), ("Todos", "*.*")]
        )
        if filename:
            self.entry_comprov_arquivo.delete(0, tk.END)
            self.entry_comprov_arquivo.insert(0, filename)
    
    def salvar_comprovante(self):
        parceiro = self.combo_comprov_parceiro.get()
        loja = self.combo_comprov_loja.get()
        
        if not parceiro or not loja:
            messagebox.showwarning("Atenção", "Selecione parceiro e loja!")
            return
        
        parceiro_id = int(parceiro.split(' - ')[0])
        loja_id = int(loja.split(' - ')[0])
        
        data = self.entry_comprov_data.get()
        assinatura = self.entry_comprov_assinatura.get()
        arquivo = self.entry_comprov_arquivo.get()
        
        try:
            qtd_20l = int(self.entry_comprov_qtd_20l.get() or 0)
            qtd_10l = int(self.entry_comprov_qtd_10l.get() or 0)
            qtd_cx_copo = int(self.entry_comprov_qtd_cx_copo.get() or 0)
            qtd_1500ml = int(self.entry_comprov_qtd_1500ml.get() or 0)
        except ValueError:
            messagebox.showerror("Erro", "Quantidades inválidas!")
            return
        
        # Converter data
        try:
            data_obj = datetime.strptime(data, '%d/%m/%Y')
            data_sql = data_obj.strftime('%Y-%m-%d')
        except:
            messagebox.showerror("Erro", "Data inválida! Use o formato DD/MM/AAAA")
            return
        
        self.cursor.execute("""
            INSERT INTO comprovantes (parceiro_id, loja_id, data_entrega, qtd_20l, qtd_10l,
                                     qtd_cx_copo, qtd_1500ml, assinatura, arquivo_comprovante)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (parceiro_id, loja_id, data_sql, qtd_20l, qtd_10l, qtd_cx_copo, qtd_1500ml, assinatura, arquivo))
        
        self.conn.commit()
        messagebox.showinfo("Sucesso", "Comprovante registrado!")
        self.limpar_comprovante()
        self.carregar_comprovantes()
        self.atualizar_dashboard()
    
    def limpar_comprovante(self):
        self.combo_comprov_parceiro.set('')
        self.combo_comprov_loja.set('')
        self.entry_comprov_data.delete(0, tk.END)
        self.entry_comprov_data.insert(0, datetime.now().strftime('%d/%m/%Y'))
        self.entry_comprov_assinatura.delete(0, tk.END)
        self.entry_comprov_qtd_20l.delete(0, tk.END)
        self.entry_comprov_qtd_20l.insert(0, '0')
        self.entry_comprov_qtd_10l.delete(0, tk.END)
        self.entry_comprov_qtd_10l.insert(0, '0')
        self.entry_comprov_qtd_cx_copo.delete(0, tk.END)
        self.entry_comprov_qtd_cx_copo.insert(0, '0')
        self.entry_comprov_qtd_1500ml.delete(0, tk.END)
        self.entry_comprov_qtd_1500ml.insert(0, '0')
        self.entry_comprov_arquivo.delete(0, tk.END)
    
    def carregar_comprovantes(self):
        for item in self.tree_comprovantes.get_children():
            self.tree_comprovantes.delete(item)
        
        self.cursor.execute("""
            SELECT c.id, c.data_entrega, p.nome_parceiro, l.nome,
                   c.qtd_20l, c.qtd_10l, c.qtd_cx_copo, c.qtd_1500ml
            FROM comprovantes c
            JOIN parceiros p ON c.parceiro_id = p.id
            JOIN lojas l ON c.loja_id = l.id
            ORDER BY c.data_entrega DESC
        """)
        
        for row in self.cursor.fetchall():
            data_format = datetime.strptime(row[1], '%Y-%m-%d').strftime('%d/%m/%Y')
            values = (row[0], data_format, row[2], row[3], row[4], row[5], row[6], row[7])
            self.tree_comprovantes.insert('', 'end', values=values)
    
    def excluir_comprovante(self):
        selected = self.tree_comprovantes.selection()
        if not selected:
            messagebox.showwarning("Atenção", "Selecione um comprovante!")
            return
        
        if messagebox.askyesno("Confirmar", "Deseja realmente excluir este comprovante?"):
            item = self.tree_comprovantes.item(selected[0])
            comprovante_id = item['values'][0]
            
            self.cursor.execute("DELETE FROM comprovantes WHERE id = ?", (comprovante_id,))
            self.conn.commit()
            messagebox.showinfo("Sucesso", "Comprovante excluído!")
            self.carregar_comprovantes()
            self.atualizar_dashboard()
    
    # === MÉTODOS DE RELATÓRIOS ===
    def atualizar_combo_marcas_relatorio(self):
        self.cursor.execute("SELECT id, nome FROM marcas ORDER BY nome")
        marcas = self.cursor.fetchall()
        self.combo_rel_marca['values'] = [f"{m[0]} - {m[1]}" for m in marcas]
    
    def atualizar_combo_parceiros_relatorio(self):
        self.cursor.execute("SELECT id, nome_parceiro FROM parceiros ORDER BY nome_parceiro")
        parceiros = self.cursor.fetchall()
        self.combo_rel_parceiro['values'] = [f"{p[0]} - {p[1]}" for p in parceiros]
    
    def gerar_relatorio_marca(self):
        marca = self.combo_rel_marca.get()
        if not marca:
            messagebox.showwarning("Atenção", "Selecione uma marca!")
            return
        
        marca_id = int(marca.split(' - ')[0])
        data_inicio = self.entry_rel_marca_data_inicio.get()
        data_fim = self.entry_rel_marca_data_fim.get()
        
        # Limpar árvore
        for item in self.tree_rel_marca.get_children():
            self.tree_rel_marca.delete(item)
        
        # Construir query
        query = """
            SELECT l.nome, l.local_entrega, l.municipio,
                   SUM(c.qtd_20l), SUM(c.qtd_10l), SUM(c.qtd_cx_copo), SUM(c.qtd_1500ml),
                   l.valor_20l, l.valor_10l, l.valor_cx_copo, l.valor_1500ml
            FROM comprovantes c
            JOIN lojas l ON c.loja_id = l.id
            WHERE l.marca_id = ?
        """
        
        params = [marca_id]
        
        if data_inicio:
            try:
                data_obj = datetime.strptime(data_inicio, '%d/%m/%Y')
                query += " AND c.data_entrega >= ?"
                params.append(data_obj.strftime('%Y-%m-%d'))
            except:
                pass
        
        if data_fim:
            try:
                data_obj = datetime.strptime(data_fim, '%d/%m/%Y')
                query += " AND c.data_entrega <= ?"
                params.append(data_obj.strftime('%Y-%m-%d'))
            except:
                pass
        
        query += " GROUP BY l.id ORDER BY l.nome"
        
        self.cursor.execute(query, params)
        
        total_geral = 0
        for row in self.cursor.fetchall():
            nome, local, municipio, qtd_20l, qtd_10l, qtd_cx_copo, qtd_1500ml, val_20l, val_10l, val_copo, val_1500 = row
            
            total = (qtd_20l or 0) * (val_20l or 0) + \
                   (qtd_10l or 0) * (val_10l or 0) + \
                   (qtd_cx_copo or 0) * (val_copo or 0) + \
                   (qtd_1500ml or 0) * (val_1500 or 0)
            
            total_geral += total
            
            valores = (nome, local, municipio, qtd_20l or 0, qtd_10l or 0, 
                      qtd_cx_copo or 0, qtd_1500ml or 0, f"R$ {total:.2f}")
            self.tree_rel_marca.insert('', 'end', values=valores)
        
        self.lbl_total_marca.config(text=f"Total Geral: R$ {total_geral:.2f}")
    
    def gerar_relatorio_parceiro(self):
        parceiro = self.combo_rel_parceiro.get()
        if not parceiro:
            messagebox.showwarning("Atenção", "Selecione um parceiro!")
            return
        
        parceiro_id = int(parceiro.split(' - ')[0])
        data_inicio = self.entry_rel_parceiro_data_inicio.get()
        data_fim = self.entry_rel_parceiro_data_fim.get()
        
        # Limpar árvore
        for item in self.tree_rel_parceiro.get_children():
            self.tree_rel_parceiro.delete(item)
        
        # Construir query
        query = """
            SELECT l.nome, c.data_entrega,
                   c.qtd_20l, c.qtd_10l, c.qtd_cx_copo, c.qtd_1500ml,
                   p.valor_20l, p.valor_10l, p.valor_cx_copo, p.valor_1500ml
            FROM comprovantes c
            JOIN lojas l ON c.loja_id = l.id
            JOIN parceiros p ON c.parceiro_id = p.id
            WHERE c.parceiro_id = ?
        """
        
        params = [parceiro_id]
        
        if data_inicio:
            try:
                data_obj = datetime.strptime(data_inicio, '%d/%m/%Y')
                query += " AND c.data_entrega >= ?"
                params.append(data_obj.strftime('%Y-%m-%d'))
            except:
                pass
        
        if data_fim:
            try:
                data_obj = datetime.strptime(data_fim, '%d/%m/%Y')
                query += " AND c.data_entrega <= ?"
                params.append(data_obj.strftime('%Y-%m-%d'))
            except:
                pass
        
        query += " ORDER BY c.data_entrega DESC"
        
        self.cursor.execute(query, params)
        
        total_geral = 0
        for row in self.cursor.fetchall():
            nome, data, qtd_20l, qtd_10l, qtd_cx_copo, qtd_1500ml, val_20l, val_10l, val_copo, val_1500 = row
            
            total = (qtd_20l or 0) * (val_20l or 0) + \
                   (qtd_10l or 0) * (val_10l or 0) + \
                   (qtd_cx_copo or 0) * (val_copo or 0) + \
                   (qtd_1500ml or 0) * (val_1500 or 0)
            
            total_geral += total
            
            data_format = datetime.strptime(data, '%Y-%m-%d').strftime('%d/%m/%Y')
            valores = (nome, data_format, qtd_20l or 0, qtd_10l or 0,
                      qtd_cx_copo or 0, qtd_1500ml or 0, f"R$ {total:.2f}")
            self.tree_rel_parceiro.insert('', 'end', values=valores)
        
        self.lbl_total_parceiro.config(text=f"Total a Receber: R$ {total_geral:.2f}")
    
    def exportar_relatorio(self, tipo):
        messagebox.showinfo("Info", f"Exportação de relatório de {tipo} será implementada")
    
    # === MÉTODOS DO DASHBOARD ===
    def atualizar_dashboard(self):
        # Total de parceiros
        self.cursor.execute("SELECT COUNT(*) FROM parceiros")
        total_parceiros = self.cursor.fetchone()[0]
        
        # Parceiros que enviaram
        self.cursor.execute("SELECT COUNT(DISTINCT parceiro_id) FROM comprovantes")
        parceiros_enviaram = self.cursor.fetchone()[0]
        
        # Total de lojas
        self.cursor.execute("SELECT COUNT(*) FROM lojas")
        total_lojas = self.cursor.fetchone()[0]
        
        # Atualizar labels
        self.lbl_parceiros_enviaram.config(text=f"{parceiros_enviaram} / {total_parceiros}")
        self.lbl_total_lojas.config(text=str(total_lojas))
        
        # Calcular percentual de relatórios
        if total_parceiros > 0:
            percentual = (parceiros_enviaram / total_parceiros) * 100
            self.lbl_percentual_relatorios.config(text=f"{percentual:.0f}%")
        else:
            self.lbl_percentual_relatorios.config(text="0%")
        
        # Atualizar lista de parceiros
        for item in self.tree_dashboard.get_children():
            self.tree_dashboard.delete(item)
        
        self.cursor.execute("""
            SELECT p.nome_parceiro,
                   CASE WHEN c.ultima_entrega IS NOT NULL THEN 'Enviado' ELSE 'Pendente' END,
                   COALESCE(c.ultima_entrega, 'Sem entregas')
            FROM parceiros p
            LEFT JOIN (
                SELECT parceiro_id, MAX(data_entrega) as ultima_entrega
                FROM comprovantes
                GROUP BY parceiro_id
            ) c ON p.id = c.parceiro_id
            ORDER BY p.nome_parceiro
        """)
        
        for row in self.cursor.fetchall():
            nome, status, ultima = row
            if ultima != 'Sem entregas':
                try:
                    ultima = datetime.strptime(ultima, '%Y-%m-%d').strftime('%d/%m/%Y')
                except:
                    pass
            self.tree_dashboard.insert('', 'end', values=(nome, status, ultima))
    
    def __del__(self):
        """Fecha a conexão ao destruir o objeto"""
        if hasattr(self, 'conn'):
            self.conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = SistemaEntregas(root)
    root.mainloop()
