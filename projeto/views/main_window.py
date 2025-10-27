"""Tkinter-based graphical interface for the gestão de parceiros app."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk


class MainWindow:
    """Desktop window that organises forms, tables and dashboards."""

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Gestão de Parceiros")
        self.root.geometry("1180x820")
        self.root.minsize(1024, 720)

        self.status_var = tk.StringVar(value="Bem-vindo ao sistema de gestão de parceiros.")

        self._configure_styles()
        self._create_layout()

    def _configure_styles(self) -> None:
        """Initialise ttk styles for a cleaner appearance."""
        style = ttk.Style(self.root)
        if "clam" in style.theme_names():
            style.theme_use("clam")

        style.configure("Card.TLabelframe", padding=16)
        style.configure("Card.TLabelframe.Label", font=("Segoe UI", 12, "bold"))
        style.configure("Heading.TLabel", font=("Segoe UI", 14, "bold"))
        style.configure("Section.TLabel", font=("Segoe UI", 11, "bold"))

    def _create_layout(self) -> None:
        """Compose the notebook-based layout for the application."""
        main_container = ttk.Frame(self.root, padding=20)
        main_container.pack(fill=tk.BOTH, expand=True)

        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self._build_loja_tab()
        self._build_parceiro_tab()
        self._build_relatorios_tab()
        self._build_dashboard_tab()

        log_frame = ttk.LabelFrame(main_container, text="Central de mensagens", style="Card.TLabelframe")
        log_frame.pack(fill=tk.BOTH, expand=False, pady=(20, 0))

        self.log_text = tk.Text(log_frame, height=5, wrap="word", state="disabled", font=("Segoe UI", 10))
        self.log_text.pack(fill=tk.BOTH, expand=True)

        status_bar = ttk.Frame(self.root, padding=(20, 10))
        status_bar.pack(fill=tk.X)
        status_label = ttk.Label(status_bar, textvariable=self.status_var)
        status_label.pack(side=tk.LEFT)

    # ------------------------------------------------------------------
    # Loja
    # ------------------------------------------------------------------
    def _build_loja_tab(self) -> None:
        loja_frame = ttk.Frame(self.notebook, padding=20)
        loja_frame.columnconfigure(0, weight=1)
        loja_frame.columnconfigure(1, weight=1)
        loja_frame.rowconfigure(2, weight=1)
        self.notebook.add(loja_frame, text="Loja")

        marca_frame = ttk.LabelFrame(loja_frame, text="Cadastro da Marca", style="Card.TLabelframe")
        marca_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 12), pady=(0, 20))
        marca_frame.columnconfigure(1, weight=1)

        self._create_labeled_entry(marca_frame, "Nome da marca:", 0)
        self._create_labeled_entry(marca_frame, "Código Disagua:", 1)
        ttk.Button(marca_frame, text="Salvar marca").grid(row=2, column=0, columnspan=2, pady=(12, 0), sticky="e")

        loja_form_frame = ttk.LabelFrame(loja_frame, text="Cadastro da Loja", style="Card.TLabelframe")
        loja_form_frame.grid(row=0, column=1, sticky="nsew", pady=(0, 20))
        for col in range(4):
            loja_form_frame.columnconfigure(col, weight=1)

        loja_fields = [
            "Nome da loja:",
            "Código Disagua:",
            "Local de entrega:",
            "Município:",
            "Estado:",
            "Valor 20L:",
            "Valor 10L:",
            "Valor Caixa Copo:",
            "Valor 1500ml:",
        ]
        for index, label in enumerate(loja_fields):
            row, col = divmod(index, 2)
            current_row = row
            current_col = col * 2
            ttk.Label(loja_form_frame, text=label).grid(row=current_row, column=current_col, sticky="w", pady=4, padx=(0, 8))
            entry = ttk.Entry(loja_form_frame)
            entry.grid(row=current_row, column=current_col + 1, sticky="ew", pady=4)

        ttk.Button(loja_form_frame, text="Registrar loja").grid(row=5, column=3, sticky="e", pady=(12, 0))

        gerenciamento_frame = ttk.LabelFrame(loja_frame, text="Gerenciamento da Loja", style="Card.TLabelframe")
        gerenciamento_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        gerenciamento_frame.columnconfigure(1, weight=1)

        ttk.Label(
            gerenciamento_frame,
            text=(
                "Atualize rapidamente os dados cadastrais e os valores praticados nas entregas. "
                "Selecione a loja desejada e ajuste os campos antes de salvar."
            ),
            wraplength=860,
        ).grid(row=0, column=0, columnspan=2, sticky="w")
        ttk.Combobox(gerenciamento_frame, values=("Loja 1", "Loja 2"), state="readonly").grid(
            row=1, column=0, sticky="ew", pady=8
        )
        ttk.Button(gerenciamento_frame, text="Atualizar informações").grid(row=1, column=1, sticky="e", padx=(12, 0))

        consumo_frame = ttk.LabelFrame(loja_frame, text="Consumo da Loja", style="Card.TLabelframe")
        consumo_frame.grid(row=2, column=0, columnspan=2, sticky="nsew")
        consumo_frame.columnconfigure(0, weight=1)
        consumo_frame.rowconfigure(0, weight=1)

        columns = ("data", "produto", "quantidade", "valor")
        consumo_tree = ttk.Treeview(consumo_frame, columns=columns, show="headings", height=6)
        consumo_tree.heading("data", text="Data")
        consumo_tree.heading("produto", text="Produto")
        consumo_tree.heading("quantidade", text="Quantidade")
        consumo_tree.heading("valor", text="Valor total")
        consumo_tree.column("data", width=100, anchor="center")
        consumo_tree.column("produto", width=160)
        consumo_tree.column("quantidade", width=110, anchor="center")
        consumo_tree.column("valor", width=120, anchor="e")

        sample_consumo = [
            ("03/01/2024", "Galão 20L", "35", "R$ 1.225,00"),
            ("05/01/2024", "Galão 10L", "48", "R$ 960,00"),
            ("08/01/2024", "Caixa Copo", "20", "R$ 420,00"),
        ]
        for record in sample_consumo:
            consumo_tree.insert("", tk.END, values=record)

        consumo_tree.grid(row=0, column=0, sticky="nsew")
        consumo_scroll = ttk.Scrollbar(consumo_frame, orient=tk.VERTICAL, command=consumo_tree.yview)
        consumo_tree.configure(yscrollcommand=consumo_scroll.set)
        consumo_scroll.grid(row=0, column=1, sticky="ns")

        ttk.Label(
            consumo_frame,
            text=(
                "Recepção de comprovantes e conferência: preencha com o nome da loja, "
                "local de entrega, produto, quantidade, data e assinatura para validar as entregas."
            ),
            wraplength=860,
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(12, 0))

    # ------------------------------------------------------------------
    # Parceiro
    # ------------------------------------------------------------------
    def _build_parceiro_tab(self) -> None:
        parceiro_frame = ttk.Frame(self.notebook, padding=20)
        parceiro_frame.columnconfigure(0, weight=2)
        parceiro_frame.columnconfigure(1, weight=1)
        parceiro_frame.rowconfigure(1, weight=1)
        self.notebook.add(parceiro_frame, text="Parceiro")

        cadastro_frame = ttk.LabelFrame(parceiro_frame, text="Cadastro de Parceiro", style="Card.TLabelframe")
        cadastro_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 12), pady=(0, 20))
        for col in range(4):
            cadastro_frame.columnconfigure(col, weight=1)

        parceiro_fields = [
            "Cidade:",
            "Estado:",
            "Parceiro:",
            "Distribuidora:",
            "CNPJ:",
            "Telefone:",
            "E-mail:",
            "Dia do pagamento:",
            "Banco:",
            "Agência e conta:",
            "Chave Pix:",
            "Valor 20L:",
            "Valor 10L:",
            "Valor Caixa Copo:",
            "Valor 1500ml:",
        ]
        for index, label in enumerate(parceiro_fields):
            row, col = divmod(index, 2)
            ttk.Label(cadastro_frame, text=label).grid(row=row, column=col * 2, sticky="w", pady=4, padx=(0, 8))
            ttk.Entry(cadastro_frame).grid(row=row, column=col * 2 + 1, sticky="ew", pady=4)

        ttk.Button(cadastro_frame, text="Salvar parceiro").grid(row=8, column=3, sticky="e", pady=(12, 0))

        comprovantes_frame = ttk.LabelFrame(parceiro_frame, text="Comprovantes de Entrega", style="Card.TLabelframe")
        comprovantes_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 12))
        comprovantes_frame.columnconfigure(0, weight=1)
        comprovantes_frame.rowconfigure(0, weight=1)

        comprovantes_columns = ("data", "loja", "produto", "quantidade", "assinatura")
        comprovantes_tree = ttk.Treeview(
            comprovantes_frame,
            columns=comprovantes_columns,
            show="headings",
            height=8,
        )
        headings = {
            "data": "Data",
            "loja": "Loja",
            "produto": "Produto",
            "quantidade": "Quantidade",
            "assinatura": "Assinatura",
        }
        for column, title in headings.items():
            comprovantes_tree.heading(column, text=title)
            anchor = "center" if column in {"data", "quantidade"} else "w"
            comprovantes_tree.column(column, anchor=anchor, width=130)

        comprovantes_sample = [
            ("03/01/2024", "Loja Central", "Galão 20L", 20, "Maria Lima"),
            ("05/01/2024", "Mercado Sul", "Caixa Copo", 12, "João Freitas"),
        ]
        for item in comprovantes_sample:
            comprovantes_tree.insert("", tk.END, values=item)

        comprovantes_tree.grid(row=0, column=0, sticky="nsew")
        comprovantes_scroll = ttk.Scrollbar(
            comprovantes_frame, orient=tk.VERTICAL, command=comprovantes_tree.yview
        )
        comprovantes_tree.configure(yscrollcommand=comprovantes_scroll.set)
        comprovantes_scroll.grid(row=0, column=1, sticky="ns")

        ttk.Label(
            comprovantes_frame,
            text="Utilize esta área para validar entregas do parceiro com base nos comprovantes recebidos.",
            wraplength=620,
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(12, 0))

        lojas_frame = ttk.LabelFrame(parceiro_frame, text="Lojas na carteira", style="Card.TLabelframe")
        lojas_frame.grid(row=0, column=1, rowspan=2, sticky="nsew")
        lojas_frame.columnconfigure(0, weight=1)
        lojas_frame.rowconfigure(1, weight=1)

        ttk.Label(
            lojas_frame,
            text=(
                "As lojas são sugeridas automaticamente de acordo com o estado e a cidade do parceiro. "
                "É possível vincular outras cidades do mesmo estado para ampliar a carteira de entregas."
            ),
            wraplength=320,
        ).grid(row=0, column=0, sticky="w")

        lojas_columns = ("loja", "cidade", "estado")
        lojas_tree = ttk.Treeview(lojas_frame, columns=lojas_columns, show="headings", height=12)
        lojas_tree.heading("loja", text="Loja")
        lojas_tree.heading("cidade", text="Cidade")
        lojas_tree.heading("estado", text="Estado")
        lojas_tree.column("loja", width=160)
        lojas_tree.column("cidade", width=120)
        lojas_tree.column("estado", width=80, anchor="center")

        for loja in [
            ("Mercado Centro", "Belo Horizonte", "MG"),
            ("Super Água", "Contagem", "MG"),
            ("Hidrata Mais", "Betim", "MG"),
        ]:
            lojas_tree.insert("", tk.END, values=loja)

        lojas_tree.grid(row=1, column=0, sticky="nsew", pady=(12, 0))
        lojas_scroll = ttk.Scrollbar(lojas_frame, orient=tk.VERTICAL, command=lojas_tree.yview)
        lojas_tree.configure(yscrollcommand=lojas_scroll.set)
        lojas_scroll.grid(row=1, column=1, sticky="ns", pady=(12, 0))

        ttk.Button(lojas_frame, text="Vincular loja selecionada").grid(row=2, column=0, sticky="e", pady=(12, 0))

    # ------------------------------------------------------------------
    # Relatórios
    # ------------------------------------------------------------------
    def _build_relatorios_tab(self) -> None:
        relatorios_frame = ttk.Frame(self.notebook, padding=20)
        relatorios_frame.columnconfigure(0, weight=1)
        relatorios_frame.columnconfigure(1, weight=1)
        self.notebook.add(relatorios_frame, text="Relatórios")

        marca_report = ttk.LabelFrame(relatorios_frame, text="Relatório da Marca", style="Card.TLabelframe")
        marca_report.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        marca_report.columnconfigure(0, weight=1)
        marca_report.rowconfigure(0, weight=1)

        marca_columns = ("periodo", "produto", "quantidade", "valor")
        marca_tree = ttk.Treeview(marca_report, columns=marca_columns, show="headings", height=10)
        marca_tree.heading("periodo", text="Período")
        marca_tree.heading("produto", text="Produto")
        marca_tree.heading("quantidade", text="Quantidade")
        marca_tree.heading("valor", text="Total Marca")
        marca_tree.column("periodo", width=120, anchor="center")
        marca_tree.column("produto", width=160)
        marca_tree.column("quantidade", width=110, anchor="center")
        marca_tree.column("valor", width=120, anchor="e")

        marca_tree.grid(row=0, column=0, sticky="nsew")
        marca_scroll = ttk.Scrollbar(marca_report, orient=tk.VERTICAL, command=marca_tree.yview)
        marca_tree.configure(yscrollcommand=marca_scroll.set)
        marca_scroll.grid(row=0, column=1, sticky="ns")

        ttk.Label(
            marca_report,
            text=(
                "O relatório utiliza os preços cadastrados na marca para totalizar os produtos entregues "
                "com base nos comprovantes recebidos."
            ),
            wraplength=360,
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(12, 0))

        parceiro_report = ttk.LabelFrame(relatorios_frame, text="Relatório do Parceiro", style="Card.TLabelframe")
        parceiro_report.grid(row=0, column=1, sticky="nsew")
        parceiro_report.columnconfigure(0, weight=1)
        parceiro_report.rowconfigure(0, weight=1)

        parceiro_columns = ("periodo", "produto", "quantidade", "valor")
        parceiro_tree = ttk.Treeview(parceiro_report, columns=parceiro_columns, show="headings", height=10)
        parceiro_tree.heading("periodo", text="Período")
        parceiro_tree.heading("produto", text="Produto")
        parceiro_tree.heading("quantidade", text="Quantidade")
        parceiro_tree.heading("valor", text="Total Parceiro")
        parceiro_tree.column("periodo", width=120, anchor="center")
        parceiro_tree.column("produto", width=160)
        parceiro_tree.column("quantidade", width=110, anchor="center")
        parceiro_tree.column("valor", width=120, anchor="e")

        parceiro_tree.grid(row=0, column=0, sticky="nsew")
        parceiro_scroll = ttk.Scrollbar(parceiro_report, orient=tk.VERTICAL, command=parceiro_tree.yview)
        parceiro_tree.configure(yscrollcommand=parceiro_scroll.set)
        parceiro_scroll.grid(row=0, column=1, sticky="ns")

        ttk.Label(
            parceiro_report,
            text="Exibe o valor total a ser repassado ao parceiro pelos serviços prestados no período selecionado.",
            wraplength=360,
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(12, 0))

    # ------------------------------------------------------------------
    # Dashboard
    # ------------------------------------------------------------------
    def _build_dashboard_tab(self) -> None:
        dashboard_frame = ttk.Frame(self.notebook, padding=20)
        dashboard_frame.columnconfigure(0, weight=1)
        dashboard_frame.columnconfigure(1, weight=1)
        self.notebook.add(dashboard_frame, text="Dashboard")

        farol_frame = ttk.LabelFrame(dashboard_frame, text="Farol de parceiros", style="Card.TLabelframe")
        farol_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        farol_frame.columnconfigure(0, weight=1)
        farol_frame.rowconfigure(0, weight=1)

        farol_columns = ("parceiro", "status")
        farol_tree = ttk.Treeview(farol_frame, columns=farol_columns, show="headings", height=12)
        farol_tree.heading("parceiro", text="Parceiro")
        farol_tree.heading("status", text="Envio de comprovantes")
        farol_tree.column("parceiro", width=200)
        farol_tree.column("status", width=180)

        for parceiro, status in [
            ("Água Norte", "Enviado"),
            ("Distribuidora Sul", "Pendente"),
            ("Hidrata Express", "Em análise"),
        ]:
            farol_tree.insert("", tk.END, values=(parceiro, status))

        farol_tree.grid(row=0, column=0, sticky="nsew")
        farol_scroll = ttk.Scrollbar(farol_frame, orient=tk.VERTICAL, command=farol_tree.yview)
        farol_tree.configure(yscrollcommand=farol_scroll.set)
        farol_scroll.grid(row=0, column=1, sticky="ns")

        percentual_frame = ttk.LabelFrame(
            dashboard_frame, text="Preenchimento dos relatórios", style="Card.TLabelframe"
        )
        percentual_frame.grid(row=0, column=1, sticky="nsew")
        percentual_frame.columnconfigure(0, weight=1)

        ttk.Label(
            percentual_frame,
            text="Percentual do relatório preenchido",
            style="Section.TLabel",
        ).grid(row=0, column=0, sticky="w")

        self.report_progress = ttk.Progressbar(percentual_frame, orient=tk.HORIZONTAL, length=200, mode="determinate")
        self.report_progress.grid(row=1, column=0, sticky="ew", pady=(12, 0))
        self.report_progress['value'] = 65

        ttk.Label(
            percentual_frame,
            text=(
                "Acompanhe o envio dos comprovantes e a consolidação das informações para garantir que "
                "os relatórios estejam completos antes do fechamento do período."
            ),
            wraplength=320,
        ).grid(row=2, column=0, sticky="w", pady=(12, 0))

    # ------------------------------------------------------------------
    # Utility helpers
    # ------------------------------------------------------------------
    def _create_labeled_entry(self, parent: ttk.Widget, label_text: str, row: int) -> ttk.Entry:
        """Create a label and entry pair inside a grid-based container."""
        ttk.Label(parent, text=label_text).grid(row=row, column=0, sticky="w", pady=4, padx=(0, 8))
        entry = ttk.Entry(parent)
        entry.grid(row=row, column=1, sticky="ew", pady=4)
        return entry

    def append_log(self, message: str) -> None:
        """Append a message to the log area."""
        self.log_text.configure(state="normal")
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.configure(state="disabled")
        self.log_text.see(tk.END)

    def show_status(self, message: str) -> None:
        """Update the status bar text."""
        self.status_var.set(message)

    def show_message(self, message: str, title: str | None = None) -> None:
        """Show a message box to the user."""
        messagebox.showinfo(title or "Gestão de Parceiros", message)

    def run(self) -> None:
        """Start the Tk event loop."""
        self.root.mainloop()
