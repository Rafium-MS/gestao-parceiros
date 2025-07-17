#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Interface de Comprovantes
------------------------
Implementa a interface gráfica para o gerenciamento de comprovantes de entrega.
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import logging
import datetime
from PIL import Image, ImageTk
from tkcalendar import DateEntry
from controllers.comprovante_controller import ComprovanteController
from utils.validators import formatar_data
from utils.ocr_utils import extract_text_from_image, extract_text_from_pdf
from utils import carregar_combobox_por_cidade
from utils.tooltip import ToolTip
from utils.style import configurar_estilos_modernos
class ComprovanteView(ttk.Frame):
    """Interface gráfica para gerenciamento de comprovantes de entrega."""

    def __init__(self, parent, db_manager):
        """
        Inicializa a interface de comprovantes.

        Args:
            parent (tk.Widget): Widget pai.
            db_manager (DatabaseManager): Instância do gerenciador de banco de dados.
        """
        super().__init__(parent)
        self.parent = parent
        self.logger = logging.getLogger(__name__)
        self.db_manager = db_manager
        configurar_estilos_modernos()

        # Controlador
        self.controller = ComprovanteController(db_manager)

        # Diretório de comprovantes
        self.comprovantes_dir = self._obter_diretorio_comprovantes()

        # ID do comprovante atual (para edição)
        self.comprovante_atual_id = None
        self.arquivo_selecionado = None

        # Construir interface
        self._criar_widgets()
        self._configurar_eventos()

        # Carregar dados iniciais
        self._carregar_comprovantes()
        self._carregar_parceiros_combobox()
        self._carregar_lojas_combobox()

    def _obter_diretorio_comprovantes(self):
        """Obtém o diretório de comprovantes a partir da configuração."""
        try:
            # Tentar obter do arquivo de configuração
            config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.ini')
            import configparser
            config = configparser.ConfigParser()
            config.read(config_path)
            comprovantes_dir = config['COMPROVANTES']['path']

            # Verificar se o diretório existe
            if not os.path.exists(comprovantes_dir):
                os.makedirs(comprovantes_dir, exist_ok=True)

            return comprovantes_dir
        except Exception as e:
            self.logger.error(f"Erro ao obter diretório de comprovantes: {str(e)}")
            # Usar diretório padrão
            default_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'comprovantes')
            os.makedirs(default_dir, exist_ok=True)
            return default_dir

    def _criar_widgets(self):
        """Cria os widgets da interface."""
        # Frame para formulário
        self.frame_form = ttk.LabelFrame(self, text="Cadastro de Comprovantes de Entrega")
        self.frame_form.pack(fill=tk.X, padx=10, pady=10)

        # Container para organizar lado a lado
        container = ttk.Frame(self.frame_form)
        container.pack(fill=tk.X, padx=5, pady=5)

        # Lado esquerdo: Campos do formulário
        self.frame_campos = ttk.Frame(container)
        self.frame_campos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Linha 1: Parceiro e Loja
        form_row = 0
        ttk.Label(self.frame_campos, text="Parceiro:").grid(row=form_row, column=0, padx=5, pady=5, sticky=tk.W)
        self.combo_parceiro = ttk.Combobox(self.frame_campos, width=30, state="readonly")
        self.combo_parceiro.grid(row=form_row, column=1, padx=5, pady=5, sticky=tk.W)

        ttk.Label(self.frame_campos, text="Loja:").grid(row=form_row, column=2, padx=5, pady=5, sticky=tk.W)
        self.combo_loja = ttk.Combobox(self.frame_campos, width=30, state="readonly")
        self.combo_loja.grid(row=form_row, column=3, padx=5, pady=5, sticky=tk.W)

        # Linha 2: Data de Entrega
        form_row += 1
        ttk.Label(self.frame_campos, text="Data de Entrega:").grid(row=form_row, column=0, padx=5, pady=5, sticky=tk.W)
        self.entrada_data = DateEntry(self.frame_campos, width=15, background='darkblue',
                                      foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy')
        self.entrada_data.grid(row=form_row, column=1, padx=5, pady=5, sticky=tk.W)

        # Botão para selecionar arquivo
        ttk.Label(self.frame_campos, text="Arquivo:").grid(row=form_row, column=2, padx=5, pady=5, sticky=tk.W)
        self.frame_arquivo = ttk.Frame(self.frame_campos)
        self.frame_arquivo.grid(row=form_row, column=3, padx=5, pady=5, sticky=tk.W)

        self.lbl_arquivo = ttk.Label(self.frame_arquivo, text="Nenhum arquivo selecionado")
        self.lbl_arquivo.pack(side=tk.LEFT, padx=(0, 5))

        self.btn_selecionar = ttk.Button(self.frame_arquivo, text="Selecionar", command=self._selecionar_arquivo)
        self.btn_selecionar.pack(side=tk.LEFT)

        # Linha 3: Observações
        form_row += 1
        ttk.Label(self.frame_campos, text="Observações:").grid(row=form_row, column=0, padx=5, pady=5, sticky=tk.NW)
        self.texto_observacoes = tk.Text(self.frame_campos, width=50, height=4)
        self.texto_observacoes.grid(row=form_row, column=1, columnspan=3, padx=5, pady=5, sticky=tk.EW)

        # Lado direito: Prévia do comprovante
        self.frame_preview = ttk.LabelFrame(container, text="Prévia do Comprovante")
        self.frame_preview.pack(side=tk.RIGHT, fill=tk.BOTH, padx=5, pady=5, expand=True)

        self.lbl_preview = ttk.Label(self.frame_preview, text="Nenhum arquivo selecionado")
        self.lbl_preview.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Frame para botões
        self.frame_botoes = ttk.Frame(self.frame_form)
        self.frame_botoes.pack(pady=10)

        self.btn_adicionar = ttk.Button(self.frame_botoes, text="Adicionar", command=self._adicionar_comprovante)
        self.btn_adicionar.pack(side=tk.LEFT, padx=5)

        self.btn_editar = ttk.Button(self.frame_botoes, text="Salvar Edição",
                                     command=self._editar_comprovante, state=tk.DISABLED)
        self.btn_editar.pack(side=tk.LEFT, padx=5)

        self.btn_excluir = ttk.Button(self.frame_botoes, text="Excluir",
                                      command=self._excluir_comprovante, state=tk.DISABLED)
        self.btn_excluir.pack(side=tk.LEFT, padx=5)

        self.btn_visualizar = ttk.Button(self.frame_botoes, text="Visualizar",
                                         command=self._visualizar_comprovante, state=tk.DISABLED)
        self.btn_visualizar.pack(side=tk.LEFT, padx=5)

        self.btn_ocr = ttk.Button(self.frame_botoes, text="Ler OCR",
                                  command=self._ler_ocr, state=tk.DISABLED)
        self.btn_ocr.pack(side=tk.LEFT, padx=5)

        self.btn_limpar = ttk.Button(self.frame_botoes, text="Limpar", command=self._limpar_form)
        self.btn_limpar.pack(side=tk.LEFT, padx=5)

        # Frame para pesquisa
        self.frame_pesquisa = ttk.Frame(self)
        self.frame_pesquisa.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(self.frame_pesquisa, text="Filtrar por:").pack(side=tk.LEFT, padx=5)

        self.combo_filtro = ttk.Combobox(self.frame_pesquisa, width=15, values=["Parceiro", "Loja", "Data"])
        self.combo_filtro.pack(side=tk.LEFT, padx=5)
        self.combo_filtro.current(0)  # Padrão: Parceiro

        self.entrada_pesquisa = ttk.Entry(self.frame_pesquisa, width=30)
        self.entrada_pesquisa.pack(side=tk.LEFT, padx=5)

        self.btn_pesquisar = ttk.Button(self.frame_pesquisa, text="Buscar", command=self._pesquisar_comprovante)
        self.btn_pesquisar.pack(side=tk.LEFT, padx=5)

        self.btn_limpar_pesquisa = ttk.Button(self.frame_pesquisa, text="Limpar", command=self._limpar_pesquisa)
        self.btn_limpar_pesquisa.pack(side=tk.LEFT, padx=5)

        # Intervalo de datas para pesquisa
        self.frame_periodo = ttk.Frame(self.frame_pesquisa)

        ttk.Label(self.frame_periodo, text="De:").pack(side=tk.LEFT, padx=5)
        self.data_inicio = DateEntry(self.frame_periodo, width=12, background='darkblue',
                                     foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy')
        self.data_inicio.pack(side=tk.LEFT, padx=5)

        ttk.Label(self.frame_periodo, text="Até:").pack(side=tk.LEFT, padx=5)
        self.data_fim = DateEntry(self.frame_periodo, width=12, background='darkblue',
                                  foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy')
        self.data_fim.pack(side=tk.LEFT, padx=5)

        # Frame para listagem
        self.frame_lista = ttk.Frame(self)
        self.frame_lista.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Treeview para listagem
        colunas = ("id", "parceiro", "loja", "data_entrega", "arquivo", "observacoes", "data_cadastro")
        self.treeview = ttk.Treeview(self.frame_lista, columns=colunas, show="headings", selectmode="browse")

        # Definir cabeçalhos
        self.treeview.heading("id", text="ID")
        self.treeview.heading("parceiro", text="Parceiro")
        self.treeview.heading("loja", text="Loja")
        self.treeview.heading("data_entrega", text="Data de Entrega")
        self.treeview.heading("arquivo", text="Arquivo")
        self.treeview.heading("observacoes", text="Observações")
        self.treeview.heading("data_cadastro", text="Data de Cadastro")

        # Definir larguras das colunas
        self.treeview.column("id", width=50, minwidth=50)
        self.treeview.column("parceiro", width=150, minwidth=100)
        self.treeview.column("loja", width=150, minwidth=100)
        self.treeview.column("data_entrega", width=120, minwidth=100)
        self.treeview.column("arquivo", width=200, minwidth=150)
        self.treeview.column("observacoes", width=250, minwidth=150)
        self.treeview.column("data_cadastro", width=120, minwidth=100)

        # Scrollbar
        scrollbar = ttk.Scrollbar(self.frame_lista, orient=tk.VERTICAL, command=self.treeview.yview)
        self.treeview.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.treeview.pack(fill=tk.BOTH, expand=True)

        # Estilo zebra striping
        style = ttk.Style()
        style.map("Treeview", background=[("selected", "#347083")])
        style.configure("Treeview", rowheight=25)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.configure("Treeview", font=("Segoe UI", 10))

        self.treeview.tag_configure('oddrow', background='#f9f9f9')
        self.treeview.tag_configure('evenrow', background='#ffffff')

        ToolTip(self.combo_parceiro, "Selecione o parceiro que realizou a entrega.")
        ToolTip(self.combo_loja, "Selecione a loja que recebeu a entrega.")
        ToolTip(self.entrada_data, "Informe a data em que a entrega foi feita.")
        ToolTip(self.btn_selecionar, "Clique para escolher o arquivo do comprovante (imagem ou PDF).")
        ToolTip(self.lbl_arquivo, "Nome do arquivo selecionado.")
        ToolTip(self.texto_observacoes, "Adicione informações extras sobre esta entrega.")
        ToolTip(self.lbl_preview, "Pré-visualização do arquivo selecionado (imagem ou primeira página do PDF).")

        ToolTip(self.btn_adicionar, "Clique para adicionar um novo comprovante.")
        ToolTip(self.btn_editar, "Clique para salvar alterações no comprovante selecionado.")
        ToolTip(self.btn_excluir, "Clique para excluir o comprovante selecionado.")
        ToolTip(self.btn_visualizar, "Abre o arquivo no visualizador padrão do sistema.")
        ToolTip(self.btn_ocr, "Executa OCR e tenta extrair o texto do comprovante.")
        ToolTip(self.btn_limpar, "Limpa o formulário e reinicia os botões.")

        ToolTip(self.combo_filtro, "Escolha como deseja filtrar os comprovantes.")
        ToolTip(self.entrada_pesquisa, "Digite o termo de busca (nome do parceiro ou loja).")
        ToolTip(self.data_inicio, "Data inicial do intervalo de busca (aparece ao filtrar por Data).")
        ToolTip(self.data_fim, "Data final do intervalo de busca (aparece ao filtrar por Data).")
        ToolTip(self.btn_pesquisar, "Clique para buscar comprovantes conforme o filtro.")
        ToolTip(self.btn_limpar_pesquisa, "Limpa os filtros e exibe todos os comprovantes.")

    def _configurar_eventos(self):
        """Configura os eventos da interface."""
        # Evento de seleção na treeview
        self.treeview.bind("<<TreeviewSelect>>", self._on_treeview_select)

        # Evento de tecla Enter na pesquisa
        self.entrada_pesquisa.bind("<Return>", lambda event: self._pesquisar_comprovante())

        # Evento de mudança no filtro de pesquisa
        self.combo_filtro.bind("<<ComboboxSelected>>", self._on_filtro_change)

        # Combobox dinâmico por cidade
        self.combo_parceiro.bind("<<ComboboxSelected>>", self._on_parceiro_change)
        self.combo_loja.bind("<<ComboboxSelected>>", self._on_loja_change)

        # Evento de mudança na seleção de arquivo
        self.combo_filtro.bind("<<ComboboxSelected>>", self._on_filtro_change)

        # Teclas de atalho
        self.bind("<Escape>", lambda event: self._limpar_form())

        # Botão OCR habilitado com tecla Ctrl+O
        self.bind_all('<Control-o>', lambda event: self._ler_ocr())

    def _on_filtro_change(self, event=None):
        """Manipula a mudança de filtro de pesquisa."""
        filtro = self.combo_filtro.get()

        # Mostrar/ocultar campos de pesquisa apropriados
        if filtro == "Data":
            self.frame_periodo.pack(side=tk.LEFT)
            self.entrada_pesquisa.pack_forget()
        else:
            self.entrada_pesquisa.pack(side=tk.LEFT, padx=5, after=self.combo_filtro)
            self.frame_periodo.pack_forget()

    def _on_treeview_select(self, event=None):
        """Manipula o evento de seleção na treeview."""
        selecao = self.treeview.selection()
        if selecao:
            # Obter dados da linha selecionada
            item = self.treeview.item(selecao[0])
            valores = item["values"]

            # Limpar formulário
            self._limpar_form()

            # Preencher formulário com dados selecionados
            self.comprovante_atual_id = valores[0]

            # Selecionar parceiro no combobox
            self._selecionar_valor_combobox(self.combo_parceiro, valores[1])

            # Selecionar loja no combobox
            self._selecionar_valor_combobox(self.combo_loja, valores[2])

            # Configurar data de entrega
            try:
                data_parts = valores[3].split('/')
                data = datetime.date(int(data_parts[2]), int(data_parts[1]), int(data_parts[0]))
                self.entrada_data.set_date(data)
            except:
                # Em caso de erro, usar a data atual
                self.entrada_data.set_date(datetime.date.today())

            # Arquivo
            self.lbl_arquivo.config(text=valores[4])
            self.arquivo_selecionado = valores[4]
            self._atualizar_preview()

            # Observações
            self.texto_observacoes.delete("1.0", tk.END)
            if valores[5]:
                self.texto_observacoes.insert("1.0", valores[5])

            # Habilitar botões de edição, exclusão e visualização
            self.btn_editar.config(state=tk.NORMAL)
            self.btn_excluir.config(state=tk.NORMAL)
            self.btn_visualizar.config(state=tk.NORMAL)
            self.btn_ocr.config(state=tk.NORMAL)

            # Desabilitar botão de adicionar
            self.btn_adicionar.config(state=tk.DISABLED)

    def _selecionar_valor_combobox(self, combobox, valor):
        """Seleciona um valor específico em um combobox."""
        valores = combobox['values']
        for i, v in enumerate(valores):
            if v == valor:
                combobox.current(i)
                return
        # Se não encontrar, deixar vazio
        combobox.set("")

    def _selecionar_arquivo(self):
        """Abre um diálogo para selecionar o arquivo de comprovante."""
        # Obter as extensões permitidas do arquivo de configuração
        try:
            config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.ini')
            import configparser
            config = configparser.ConfigParser()
            config.read(config_path)
            allowed_extensions = config['COMPROVANTES']['allowed_extensions'].split(',')

            # Formatar para o diálogo de arquivo
            filetypes = []
            for ext in allowed_extensions:
                filetypes.append((f"Arquivos {ext}", f"*{ext}"))
            filetypes.append(("Todos os arquivos", "*.*"))
        except:
            # Extensões padrão se não conseguir ler do config
            filetypes = [
                ("Imagens", "*.png *.jpg *.jpeg"),
                ("Documentos PDF", "*.pdf"),
                ("Todos os arquivos", "*.*")
            ]

        # Abrir diálogo para selecionar arquivo
        filepath = filedialog.askopenfilename(
            title="Selecionar Comprovante",
            filetypes=filetypes
        )

        if filepath:
            # Obter apenas o nome do arquivo
            filename = os.path.basename(filepath)
            self.arquivo_selecionado = filename
            self.lbl_arquivo.config(text=filename)
            self.btn_ocr.config(state=tk.NORMAL)

            # Copiar o arquivo para o diretório de comprovantes
            try:
                import shutil
                destino = os.path.join(self.comprovantes_dir, filename)
                shutil.copy2(filepath, destino)
                self.logger.info(f"Arquivo copiado para: {destino}")
            except Exception as e:
                self.logger.error(f"Erro ao copiar arquivo: {str(e)}")
                messagebox.showerror("Erro", f"Erro ao copiar arquivo: {str(e)}")

            # Atualizar preview
            self._atualizar_preview()

    def _atualizar_preview(self):
        """Atualiza a prévia do comprovante."""
        if not self.arquivo_selecionado:
            self.lbl_preview.config(text="Nenhum arquivo selecionado")
            return

        arquivo_path = os.path.join(self.comprovantes_dir, self.arquivo_selecionado)

        if not os.path.exists(arquivo_path):
            self.lbl_preview.config(text="Arquivo não encontrado")
            return

        # Verificar a extensão do arquivo
        _, ext = os.path.splitext(arquivo_path)
        ext = ext.lower()

        if ext in ['.jpg', '.jpeg', '.png']:
            try:
                # Carregar imagem
                img = Image.open(arquivo_path)

                # Redimensionar mantendo a proporção
                width, height = img.size
                max_size = 300  # Tamanho máximo para a prévia

                if width > height:
                    new_width = max_size
                    new_height = int(height * max_size / width)
                else:
                    new_height = max_size
                    new_width = int(width * max_size / height)

                img = img.resize((new_width, new_height), Image.LANCZOS)

                # Converter para PhotoImage
                photo = ImageTk.PhotoImage(img)

                # Atualizar o label
                self.lbl_preview.config(image=photo, text="")
                self.lbl_preview.image = photo  # Manter referência
            except Exception as e:
                self.logger.error(f"Erro ao carregar imagem: {str(e)}")
                self.lbl_preview.config(text=f"Erro ao carregar imagem: {str(e)}")
        elif ext == '.pdf':
            try:
                from pdf2image import convert_from_path
                pages = convert_from_path(arquivo_path, first_page=1, last_page=1)
                if pages:
                    img = pages[0]
                    width, height = img.size
                    max_size = 300

                    if width > height:
                        new_width = max_size
                        new_height = int(height * max_size / width)
                    else:
                        new_height = max_size
                        new_width = int(width * max_size / height)

                    img = img.resize((new_width, new_height), Image.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    self.lbl_preview.config(image=photo, text="")
                    self.lbl_preview.image = photo
                else:
                    self.lbl_preview.config(text="Não foi possível gerar prévia do PDF")
            except Exception as e:
                self.logger.error(f"Erro ao carregar PDF: {str(e)}")
                self.lbl_preview.config(text=f"Erro ao carregar PDF: {str(e)}")
        else:
            # Para arquivos não-imagem, mostrar ícone ou mensagem
            self.lbl_preview.config(text=f"Prévia não disponível para {ext}")

    def _obter_dados_form(self):
        """
        Obtém os dados do formulário.

        Returns:
            dict: Dicionário com os dados do formulário.
        """
        parceiro = self.combo_parceiro.get()
        loja = self.combo_loja.get()

        # Obter ID do parceiro a partir do nome
        parceiro_id = None
        for pid, pnome in self.parceiros_dict.items():
            if pnome == parceiro:
                parceiro_id = pid
                break

        # Obter ID da loja a partir do nome
        loja_id = None
        for lid, lnome in self.lojas_dict.items():
            if lnome == loja:
                loja_id = lid
                break

        return {
            'parceiro_id': parceiro_id,
            'loja_id': loja_id,
            'data_entrega': self.entrada_data.get_date().strftime('%Y-%m-%d'),
            'arquivo': self.arquivo_selecionado,
            'observacoes': self.texto_observacoes.get("1.0", tk.END).strip()
        }

    def _limpar_form(self):
        """Limpa o formulário e reseta o estado dos botões."""
        # Limpar campos
        self.combo_parceiro.set("")
        self.combo_loja.set("")
        self.entrada_data.set_date(datetime.date.today())
        self.arquivo_selecionado = None
        self.lbl_arquivo.config(text="Nenhum arquivo selecionado")
        self.texto_observacoes.delete("1.0", tk.END)

        # Limpar prévia
        self.lbl_preview.config(image="", text="Nenhum arquivo selecionado")
        if hasattr(self.lbl_preview, 'image'):
            del self.lbl_preview.image

        # Resetar ID atual
        self.comprovante_atual_id = None

        # Resetar estado dos botões
        self.btn_adicionar.config(state=tk.NORMAL)
        self.btn_editar.config(state=tk.DISABLED)
        self.btn_excluir.config(state=tk.DISABLED)
        self.btn_visualizar.config(state=tk.DISABLED)
        self.btn_ocr.config(state=tk.DISABLED)

        # Limpar seleção da treeview
        for item in self.treeview.selection():
            self.treeview.selection_remove(item)

    def _adicionar_comprovante(self):
        """Adiciona um novo comprovante."""
        # Obter dados do formulário
        dados = self._obter_dados_form()

        # Validar dados básicos
        if not dados['parceiro_id']:
            messagebox.showwarning("Aviso", "Selecione um parceiro!")
            return

        if not dados['loja_id']:
            messagebox.showwarning("Aviso", "Selecione uma loja!")
            return

        if not dados['arquivo']:
            messagebox.showwarning("Aviso", "Selecione um arquivo de comprovante!")
            return

        # Validar e adicionar
        sucesso, mensagem = self.controller.adicionar_comprovante(dados)

        if sucesso:
            messagebox.showinfo("Sucesso", mensagem)
            self._limpar_form()
            self._carregar_comprovantes()
        else:
            messagebox.showerror("Erro", mensagem)

    def _editar_comprovante(self):
        """Edita o comprovante selecionado."""
        if not self.comprovante_atual_id:
            messagebox.showwarning("Aviso", "Nenhum comprovante selecionado para edição!")
            return

        # Obter dados do formulário
        dados = self._obter_dados_form()

        # Validar dados básicos
        if not dados['parceiro_id']:
            messagebox.showwarning("Aviso", "Selecione um parceiro!")
            return

        if not dados['loja_id']:
            messagebox.showwarning("Aviso", "Selecione uma loja!")
            return

        # Validar e editar
        sucesso, mensagem = self.controller.editar_comprovante(self.comprovante_atual_id, dados)

        if sucesso:
            messagebox.showinfo("Sucesso", mensagem)
            self._limpar_form()
            self._carregar_comprovantes()
        else:
            messagebox.showerror("Erro", mensagem)

    def _excluir_comprovante(self):
        """Exclui o comprovante selecionado."""
        if not self.comprovante_atual_id:
            messagebox.showwarning("Aviso", "Nenhum comprovante selecionado para exclusão!")
            return

        # Confirmar exclusão
        confirmacao = messagebox.askyesno(
            "Confirmar Exclusão",
            "Tem certeza que deseja excluir este comprovante?"
        )

        if confirmacao:
            # Excluir comprovante
            sucesso, mensagem = self.controller.excluir_comprovante(self.comprovante_atual_id)

            if sucesso:
                messagebox.showinfo("Sucesso", mensagem)
                self._limpar_form()
                self._carregar_comprovantes()
            else:
                messagebox.showerror("Erro", mensagem)

    def _visualizar_comprovante(self):
        """Abre o comprovante para visualização no aplicativo padrão."""
        if not self.arquivo_selecionado:
            messagebox.showwarning("Aviso", "Nenhum arquivo selecionado para visualização!")
            return

        arquivo_path = os.path.join(self.comprovantes_dir, self.arquivo_selecionado)

        if not os.path.exists(arquivo_path):
            messagebox.showerror("Erro", "Arquivo não encontrado!")
            return

        try:
            # Abrir com o aplicativo padrão do sistema
            import subprocess
            import sys
            import platform

            if platform.system() == 'Windows':
                os.startfile(arquivo_path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.call(['open', arquivo_path])
            else:  # Linux e outros
                subprocess.call(['xdg-open', arquivo_path])

            self.logger.info(f"Arquivo aberto para visualização: {arquivo_path}")
        except Exception as e:
            self.logger.error(f"Erro ao abrir arquivo: {str(e)}")
            messagebox.showerror("Erro", f"Erro ao abrir arquivo: {str(e)}")

    def _ler_ocr(self):
        """Extrai texto do comprovante selecionado usando OCR."""
        if not self.arquivo_selecionado:
            messagebox.showwarning("Aviso", "Nenhum arquivo selecionado!")
            return

        arquivo_path = os.path.join(self.comprovantes_dir, self.arquivo_selecionado)
        if not os.path.exists(arquivo_path):
            messagebox.showerror("Erro", "Arquivo não encontrado!")
            return

        _, ext = os.path.splitext(arquivo_path)
        ext = ext.lower()

        if ext in ['.png', '.jpg', '.jpeg']:
            texto = extract_text_from_image(arquivo_path)
        elif ext == '.pdf':
            texto = extract_text_from_pdf(arquivo_path)
        else:
            messagebox.showwarning("Aviso", f"OCR não suportado para {ext}")
            return

        if texto:
            self.texto_observacoes.delete("1.0", tk.END)
            self.texto_observacoes.insert(tk.END, texto)
            messagebox.showinfo("OCR", "Texto extraído das imagens.")
        else:
            messagebox.showwarning("OCR", "Não foi possível extrair texto.")

    def _pesquisar_comprovante(self):
        """Pesquisa comprovantes com base nos filtros selecionados."""
        filtro = self.combo_filtro.get()

        if filtro == "Data":
            # Pesquisa por intervalo de datas
            data_inicio = self.data_inicio.get_date().strftime('%Y-%m-%d')
            data_fim = self.data_fim.get_date().strftime('%Y-%m-%d')

            comprovantes = self.controller.pesquisar_comprovantes_por_periodo(data_inicio, data_fim)
        else:
            # Pesquisa por termo (parceiro ou loja)
            termo = self.entrada_pesquisa.get().strip()

            if not termo:
                self._carregar_comprovantes()
                return

            if filtro == "Parceiro":
                comprovantes = self.controller.pesquisar_comprovantes_por_parceiro(termo)
            elif filtro == "Loja":
                comprovantes = self.controller.pesquisar_comprovantes_por_loja(termo)

        # Atualizar treeview
        self._atualizar_treeview(comprovantes)

    def _limpar_pesquisa(self):
        """Limpa os campos de pesquisa e recarrega todos os comprovantes."""
        self.entrada_pesquisa.delete(0, tk.END)
        # Resetar datas para período atual
        hoje = datetime.date.today()
        self.data_inicio.set_date(datetime.date(hoje.year, hoje.month, 1))  # Primeiro dia do mês
        self.data_fim.set_date(hoje)  # Hoje
        self._carregar_comprovantes()

    def _carregar_comprovantes(self):
        """Carrega todos os comprovantes na treeview."""
        comprovantes = self.controller.listar_comprovantes()
        self._atualizar_treeview(comprovantes)

    def _carregar_parceiros_combobox(self):
        """Carrega os parceiros no combobox."""
        try:
            # Obter parceiros do controller
            parceiros = self.controller.obter_parceiros_combobox()

            # Criar dicionário reverso (id -> nome) para uso interno
            self.parceiros_dict = {id: nome for nome, id in parceiros.items()}

            # Configurar valores do combobox
            self.combo_parceiro['values'] = list(parceiros.keys())

        except Exception as e:
            self.logger.error(f"Erro ao carregar parceiros para combobox: {str(e)}")
            messagebox.showerror("Erro", f"Erro ao carregar parceiros: {str(e)}")

    def _carregar_lojas_combobox(self):
        """Carrega as lojas no combobox."""
        try:
            # Obter lojas do controller␊
            lojas = self.controller.obter_lojas_combobox()

            # Criar dicionário reverso (id -> nome) para uso interno
            self.lojas_dict = {id: nome for nome, id in lojas.items()}

            # Configurar valores do combobox
            self.combo_loja['values'] = list(lojas.keys())

        except Exception as e:
            self.logger.error(f"Erro ao carregar lojas para combobox: {str(e)}")
            messagebox.showerror("Erro", f"Erro ao carregar lojas: {str(e)}")

    def _on_parceiro_change(self, event=None):
        """Filtra as lojas pela cidade do parceiro."""
        parceiro_nome = self.combo_parceiro.get()
        parceiro_id = next((pid for name, pid in self.parceiros_dict.items() if name == parceiro_nome), None)
        if parceiro_id:
            parceiro = self.controller.obter_parceiro(parceiro_id)
            if parceiro and parceiro.get("cidade"):
                lojas = carregar_combobox_por_cidade(
                    self.controller.db_manager, "lojas", parceiro["cidade"]
                )
                self.lojas_dict = {id: nome for nome, id in lojas.items()}
                self.combo_loja["values"] = list(lojas.keys())

    def _on_loja_change(self, event=None):
        """Filtra os parceiros pela cidade da loja."""
        loja_nome = self.combo_loja.get()
        loja_id = next((lid for name, lid in self.lojas_dict.items() if name == loja_nome), None)
        if loja_id:
            loja = self.controller.obter_loja(loja_id)
            if loja and loja.get("cidade"):
                parceiros = carregar_combobox_por_cidade(
                    self.controller.db_manager, "parceiros", loja["cidade"]
                )
                self.parceiros_dict = {id: nome for nome, id in parceiros.items()}
                self.combo_parceiro["values"] = list(parceiros.keys())

    def _atualizar_treeview(self, comprovantes):
        """
        Atualiza a treeview com os comprovantes fornecidos.

        Args:
            comprovantes (list): Lista de tuplas com os dados dos comprovantes.
        """
        # Limpar treeview
        for item in self.treeview.get_children():
            self.treeview.delete(item)

        # Adicionar comprovantes à treeview
        for comprovante in comprovantes:
            # Formatar a data para exibição (de YYYY-MM-DD para DD/MM/YYYY)
            data_entrega = formatar_data(comprovante[3])

            # Limitar tamanho das observações para exibição
            observacoes = comprovante[5]
            if observacoes and len(observacoes) > 50:
                observacoes = observacoes[:47] + "..."

            valores = (
                comprovante[0],  # id
                comprovante[1],  # nome do parceiro
                comprovante[2],  # nome da loja
                data_entrega,  # data de entrega formatada
                comprovante[4],  # nome do arquivo
                observacoes,  # observações (limitadas)
                comprovante[6]  # data de cadastro
            )

            tag = 'evenrow' if index % 2 == 0 else 'oddrow'
            self.treeview.insert("", "end", values=valores, tags=(tag,))

    def focus_parceiro(self):
        """Coloca o foco no campo de parceiro."""
        self.combo_parceiro.focus_set()