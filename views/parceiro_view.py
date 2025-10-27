"""
View de Parceiros.

Interface para gerenciamento completo de parceiros (CRUD).
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from controllers.parceiro_controller import ParceiroController
from utils.formatters import (
    formatar_cpf, formatar_cnpj, formatar_telefone,
    remover_formatacao, capitalizar_nome
)
from config.settings import PADDING


class ParceiroView:
    """
    Interface de gerenciamento de parceiros.
    
    Implementa CRUD completo com listagem, busca, cadastro e edição.
    """
    
    def __init__(self, parent):
        """
        Inicializa a view de parceiros.
        
        Args:
            parent: Janela pai
        """
        self.logger = logging.getLogger(__name__)
        self.controller = ParceiroController()
        self.parceiro_selecionado = None
        
        # Cria janela
        self.janela = tk.Toplevel(parent)
        self.janela.title("Gerenciamento de Parceiros")
        self.janela.geometry("1100x650")
        self.janela.minsize(900, 500)
        
        # Registra callbacks
        self.controller.registrar_callback('criar_sucesso', self.atualizar_lista)
        self.controller.registrar_callback('atualizar_sucesso', self.atualizar_lista)
        self.controller.registrar_callback('deletar_sucesso', self.atualizar_lista)
        
        # Configura interface
        self._configurar_interface()
        
        # Carrega dados iniciais
        self.atualizar_lista()
        
        self.logger.info("View de parceiros inicializada")
    
    def _configurar_interface(self):
        """Configura a interface da view."""
        # Frame principal
        frame_principal = ttk.Frame(self.janela, padding=PADDING)
        frame_principal.pack(fill=tk.BOTH, expand=True)
        
        # Título
        titulo = ttk.Label(
            frame_principal,
            text="Gerenciamento de Parceiros",
            font=("Segoe UI", 16, "bold")
        )
        titulo.pack(pady=(0, 10))
        
        # Frame de busca e ações
        frame_topo = ttk.Frame(frame_principal)
        frame_topo.pack(fill=tk.X, pady=(0, 10))
        
        # Busca
        ttk.Label(frame_topo, text="Buscar:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.entrada_busca = ttk.Entry(frame_topo, width=40)
        self.entrada_busca.pack(side=tk.LEFT, padx=5)
        self.entrada_busca.bind('<KeyRelease>', self.buscar)
        
        btn_buscar = ttk.Button(
            frame_topo,
            text="🔍 Buscar",
            command=self.buscar,
            width=12
        )
        btn_buscar.pack(side=tk.LEFT, padx=5)
        
        btn_limpar = ttk.Button(
            frame_topo,
            text="Limpar",
            command=self.limpar_busca,
            width=10
        )
        btn_limpar.pack(side=tk.LEFT, padx=5)
        
        # Botões de ação
        btn_novo = ttk.Button(
            frame_topo,
            text="➕ Novo",
            command=self.abrir_formulario_novo,
            width=12
        )
        btn_novo.pack(side=tk.RIGHT, padx=5)
        
        btn_editar = ttk.Button(
            frame_topo,
            text="✏️ Editar",
            command=self.abrir_formulario_editar,
            width=12
        )
        btn_editar.pack(side=tk.RIGHT, padx=5)
        
        btn_deletar = ttk.Button(
            frame_topo,
            text="🗑️ Deletar",
            command=self.deletar_parceiro,
            width=12
        )
        btn_deletar.pack(side=tk.RIGHT, padx=5)
        
        # Frame da tabela com scrollbar
        frame_tabela = ttk.Frame(frame_principal)
        frame_tabela.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        scroll_y = ttk.Scrollbar(frame_tabela, orient="vertical")
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        scroll_x = ttk.Scrollbar(frame_tabela, orient="horizontal")
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Tabela (Treeview)
        colunas = ("ID", "Nome", "Tipo Doc", "Documento", "Email", "Telefone", 
                   "Cidade", "Estado", "Tipo", "Status")
        
        self.tabela = ttk.Treeview(
            frame_tabela,
            columns=colunas,
            show="headings",
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set
        )
        
        scroll_y.config(command=self.tabela.yview)
        scroll_x.config(command=self.tabela.xview)
        
        # Configuração das colunas
        larguras = {
            "ID": 50,
            "Nome": 180,
            "Tipo Doc": 80,
            "Documento": 140,
            "Email": 180,
            "Telefone": 120,
            "Cidade": 120,
            "Estado": 60,
            "Tipo": 100,
            "Status": 80
        }
        
        for col in colunas:
            self.tabela.heading(col, text=col, command=lambda c=col: self.ordenar_por_coluna(c))
            self.tabela.column(col, width=larguras.get(col, 100), anchor="w")
        
        self.tabela.pack(fill=tk.BOTH, expand=True)
        
        # Bind para duplo clique
        self.tabela.bind('<Double-Button-1>', lambda e: self.abrir_formulario_editar())
        
        # Rodapé com estatísticas
        self.frame_rodape = ttk.Frame(frame_principal)
        self.frame_rodape.pack(fill=tk.X, pady=(10, 0))
        
        self.label_total = ttk.Label(self.frame_rodape, text="Total: 0 parceiros")
        self.label_total.pack(side=tk.LEFT)
        
        self.label_ativos = ttk.Label(self.frame_rodape, text="Ativos: 0")
        self.label_ativos.pack(side=tk.LEFT, padx=(20, 0))
    
    def atualizar_lista(self, *args):
        """Atualiza a lista de parceiros na tabela."""
        try:
            # Limpa tabela
            for item in self.tabela.get_children():
                self.tabela.delete(item)
            
            # Busca parceiros
            sucesso, parceiros = self.controller.listar_parceiros()
            
            if sucesso:
                for parceiro in parceiros:
                    # Formata documento
                    documento = parceiro.get('documento', '')
                    if parceiro.get('tipo_documento') == 'CPF':
                        documento_formatado = formatar_cpf(documento)
                    else:
                        documento_formatado = formatar_cnpj(documento)
                    
                    # Formata telefone
                    telefone = formatar_telefone(parceiro.get('telefone', ''))
                    
                    # Insere na tabela
                    valores = (
                        parceiro.get('id', ''),
                        parceiro.get('nome', ''),
                        parceiro.get('tipo_documento', ''),
                        documento_formatado,
                        parceiro.get('email', ''),
                        telefone,
                        parceiro.get('cidade', ''),
                        parceiro.get('estado', ''),
                        parceiro.get('tipo_parceiro', ''),
                        parceiro.get('status', '')
                    )
                    
                    self.tabela.insert('', tk.END, values=valores)
                
                # Atualiza estatísticas
                estatisticas = self.controller.obter_estatisticas()
                self.label_total.config(text=f"Total: {estatisticas.get('total', 0)} parceiros")
                self.label_ativos.config(text=f"Ativos: {estatisticas.get('ativos', 0)}")
                
            self.logger.info("Lista de parceiros atualizada")
            
        except Exception as e:
            self.logger.error(f"Erro ao atualizar lista: {e}")
            messagebox.showerror("Erro", f"Erro ao atualizar lista: {str(e)}")
    
    def buscar(self, event=None):
        """Realiza busca de parceiros."""
        termo = self.entrada_busca.get().strip()
        
        if not termo:
            self.atualizar_lista()
            return
        
        try:
            # Limpa tabela
            for item in self.tabela.get_children():
                self.tabela.delete(item)
            
            # Busca
            sucesso, parceiros = self.controller.pesquisar_parceiros(termo)
            
            if sucesso:
                for parceiro in parceiros:
                    # Formata dados (mesmo código da atualizar_lista)
                    documento = parceiro.get('documento', '')
                    if parceiro.get('tipo_documento') == 'CPF':
                        documento_formatado = formatar_cpf(documento)
                    else:
                        documento_formatado = formatar_cnpj(documento)
                    
                    telefone = formatar_telefone(parceiro.get('telefone', ''))
                    
                    valores = (
                        parceiro.get('id', ''),
                        parceiro.get('nome', ''),
                        parceiro.get('tipo_documento', ''),
                        documento_formatado,
                        parceiro.get('email', ''),
                        telefone,
                        parceiro.get('cidade', ''),
                        parceiro.get('estado', ''),
                        parceiro.get('tipo_parceiro', ''),
                        parceiro.get('status', '')
                    )
                    
                    self.tabela.insert('', tk.END, values=valores)
                
                self.logger.info(f"Busca realizada: {len(parceiros)} resultados")
            
        except Exception as e:
            self.logger.error(f"Erro ao buscar: {e}")
            messagebox.showerror("Erro", f"Erro ao buscar: {str(e)}")
    
    def limpar_busca(self):
        """Limpa o campo de busca e recarrega todos os parceiros."""
        self.entrada_busca.delete(0, tk.END)
        self.atualizar_lista()
    
    def ordenar_por_coluna(self, coluna):
        """
        Ordena a tabela por uma coluna.
        
        Args:
            coluna: Nome da coluna para ordenar
        """
        # TODO: Implementar ordenação
        pass
    
    def abrir_formulario_novo(self):
        """Abre formulário para novo parceiro."""
        FormularioParceiro(self.janela, self.controller, self)
    
    def abrir_formulario_editar(self):
        """Abre formulário para editar parceiro selecionado."""
        selecionado = self.tabela.selection()
        
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um parceiro para editar")
            return
        
        # Obtém ID do parceiro
        item = self.tabela.item(selecionado[0])
        id_parceiro = int(item['values'][0])
        
        # Busca dados completos
        sucesso, parceiro = self.controller.buscar_parceiro(id_parceiro)
        
        if sucesso:
            FormularioParceiro(self.janela, self.controller, self, parceiro)
        else:
            messagebox.showerror("Erro", "Parceiro não encontrado")
    
    def deletar_parceiro(self):
        """Deleta o parceiro selecionado."""
        selecionado = self.tabela.selection()
        
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um parceiro para deletar")
            return
        
        # Obtém dados do parceiro
        item = self.tabela.item(selecionado[0])
        id_parceiro = int(item['values'][0])
        nome_parceiro = item['values'][1]
        
        # Confirma exclusão
        if not messagebox.askyesno(
            "Confirmar Exclusão",
            f"Deseja realmente deletar o parceiro '{nome_parceiro}'?\n\n"
            "Esta ação não pode ser desfeita."
        ):
            return
        
        # Deleta
        sucesso, mensagem = self.controller.deletar_parceiro(id_parceiro)
        
        if sucesso:
            messagebox.showinfo("Sucesso", mensagem)
            self.atualizar_lista()
        else:
            messagebox.showerror("Erro", mensagem)


class FormularioParceiro:
    """Formulário para cadastro e edição de parceiros."""
    
    def __init__(self, parent, controller, view_pai, parceiro=None):
        """
        Inicializa o formulário.
        
        Args:
            parent: Janela pai
            controller: Controller de parceiros
            view_pai: View pai para atualização
            parceiro: Dados do parceiro (None para novo)
        """
        self.controller = controller
        self.view_pai = view_pai
        self.parceiro = parceiro
        self.modo_edicao = parceiro is not None
        
        # Cria janela
        self.janela = tk.Toplevel(parent)
        titulo = "Editar Parceiro" if self.modo_edicao else "Novo Parceiro"
        self.janela.title(titulo)
        self.janela.geometry("600x680")
        self.janela.resizable(False, False)
        
        # Modal
        self.janela.transient(parent)
        self.janela.grab_set()
        
        # Configura interface
        self._configurar_interface()
        
        # Preenche dados se for edição
        if self.modo_edicao:
            self._preencher_dados()
    
    def _configurar_interface(self):
        """Configura a interface do formulário."""
        # Frame principal com scroll
        canvas = tk.Canvas(self.janela)
        scrollbar = ttk.Scrollbar(self.janela, orient="vertical", command=canvas.yview)
        frame_scroll = ttk.Frame(canvas)
        
        frame_scroll.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=frame_scroll, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Frame de conteúdo
        frame = ttk.Frame(frame_scroll, padding=PADDING)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        titulo = "Editar Parceiro" if self.modo_edicao else "Novo Parceiro"
        ttk.Label(
            frame,
            text=titulo,
            font=("Segoe UI", 14, "bold")
        ).grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Campos
        row = 1
        
        # Nome
        ttk.Label(frame, text="*Nome:").grid(row=row, column=0, sticky="w", pady=5)
        self.entrada_nome = ttk.Entry(frame, width=50)
        self.entrada_nome.grid(row=row, column=1, sticky="ew", pady=5)
        row += 1
        
        # Tipo de Documento
        ttk.Label(frame, text="*Tipo Documento:").grid(row=row, column=0, sticky="w", pady=5)
        self.combo_tipo_doc = ttk.Combobox(
            frame,
            values=self.controller.obter_tipos_documento(),
            state="readonly",
            width=48
        )
        self.combo_tipo_doc.grid(row=row, column=1, sticky="ew", pady=5)
        self.combo_tipo_doc.bind('<<ComboboxSelected>>', self._atualizar_placeholder_documento)
        row += 1
        
        # Documento
        ttk.Label(frame, text="*Documento:").grid(row=row, column=0, sticky="w", pady=5)
        self.entrada_documento = ttk.Entry(frame, width=50)
        self.entrada_documento.grid(row=row, column=1, sticky="ew", pady=5)
        row += 1
        
        # Email
        ttk.Label(frame, text="Email:").grid(row=row, column=0, sticky="w", pady=5)
        self.entrada_email = ttk.Entry(frame, width=50)
        self.entrada_email.grid(row=row, column=1, sticky="ew", pady=5)
        row += 1
        
        # Telefone
        ttk.Label(frame, text="Telefone:").grid(row=row, column=0, sticky="w", pady=5)
        self.entrada_telefone = ttk.Entry(frame, width=50)
        self.entrada_telefone.grid(row=row, column=1, sticky="ew", pady=5)
        row += 1
        
        # Separador
        ttk.Separator(frame, orient="horizontal").grid(row=row, column=0, columnspan=2, sticky="ew", pady=15)
        row += 1
        
        # Endereço
        ttk.Label(frame, text="Endereço:").grid(row=row, column=0, sticky="w", pady=5)
        self.entrada_endereco = ttk.Entry(frame, width=50)
        self.entrada_endereco.grid(row=row, column=1, sticky="ew", pady=5)
        row += 1
        
        # Cidade
        ttk.Label(frame, text="Cidade:").grid(row=row, column=0, sticky="w", pady=5)
        self.entrada_cidade = ttk.Entry(frame, width=50)
        self.entrada_cidade.grid(row=row, column=1, sticky="ew", pady=5)
        row += 1
        
        # Estado
        ttk.Label(frame, text="Estado:").grid(row=row, column=0, sticky="w", pady=5)
        estados = ['AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA',
                   'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN',
                   'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO']
        self.combo_estado = ttk.Combobox(frame, values=estados, width=48)
        self.combo_estado.grid(row=row, column=1, sticky="ew", pady=5)
        row += 1
        
        # CEP
        ttk.Label(frame, text="CEP:").grid(row=row, column=0, sticky="w", pady=5)
        self.entrada_cep = ttk.Entry(frame, width=50)
        self.entrada_cep.grid(row=row, column=1, sticky="ew", pady=5)
        row += 1
        
        # Separador
        ttk.Separator(frame, orient="horizontal").grid(row=row, column=0, columnspan=2, sticky="ew", pady=15)
        row += 1
        
        # Tipo de Parceiro
        ttk.Label(frame, text="*Tipo Parceiro:").grid(row=row, column=0, sticky="w", pady=5)
        self.combo_tipo_parceiro = ttk.Combobox(
            frame,
            values=self.controller.obter_tipos_parceiro(),
            state="readonly",
            width=48
        )
        self.combo_tipo_parceiro.grid(row=row, column=1, sticky="ew", pady=5)
        row += 1
        
        # Status
        ttk.Label(frame, text="Status:").grid(row=row, column=0, sticky="w", pady=5)
        self.combo_status = ttk.Combobox(
            frame,
            values=self.controller.obter_status_disponiveis(),
            state="readonly",
            width=48
        )
        self.combo_status.grid(row=row, column=1, sticky="ew", pady=5)
        self.combo_status.set("Ativo")
        row += 1
        
        # Observações
        ttk.Label(frame, text="Observações:").grid(row=row, column=0, sticky="nw", pady=5)
        self.texto_obs = tk.Text(frame, width=38, height=4)
        self.texto_obs.grid(row=row, column=1, sticky="ew", pady=5)
        row += 1
        
        # Frame de botões
        frame_botoes = ttk.Frame(frame)
        frame_botoes.grid(row=row, column=0, columnspan=2, pady=20)
        
        btn_salvar = ttk.Button(
            frame_botoes,
            text="💾 Salvar",
            command=self.salvar,
            width=15
        )
        btn_salvar.pack(side=tk.LEFT, padx=5)
        
        btn_cancelar = ttk.Button(
            frame_botoes,
            text="✖️ Cancelar",
            command=self.janela.destroy,
            width=15
        )
        btn_cancelar.pack(side=tk.LEFT, padx=5)
        
        # Ajusta peso das colunas
        frame.columnconfigure(1, weight=1)
    
    def _preencher_dados(self):
        """Preenche o formulário com dados do parceiro."""
        if not self.parceiro:
            return
        
        self.entrada_nome.insert(0, self.parceiro.get('nome', ''))
        self.combo_tipo_doc.set(self.parceiro.get('tipo_documento', ''))
        
        # Formata documento para exibição
        documento = self.parceiro.get('documento', '')
        if self.parceiro.get('tipo_documento') == 'CPF':
            documento = formatar_cpf(documento)
        else:
            documento = formatar_cnpj(documento)
        self.entrada_documento.insert(0, documento)
        
        self.entrada_email.insert(0, self.parceiro.get('email', ''))
        
        telefone = formatar_telefone(self.parceiro.get('telefone', ''))
        self.entrada_telefone.insert(0, telefone)
        
        self.entrada_endereco.insert(0, self.parceiro.get('endereco', ''))
        self.entrada_cidade.insert(0, self.parceiro.get('cidade', ''))
        self.combo_estado.set(self.parceiro.get('estado', ''))
        self.entrada_cep.insert(0, self.parceiro.get('cep', ''))
        self.combo_tipo_parceiro.set(self.parceiro.get('tipo_parceiro', ''))
        self.combo_status.set(self.parceiro.get('status', 'Ativo'))
        self.texto_obs.insert('1.0', self.parceiro.get('observacoes', ''))
    
    def _atualizar_placeholder_documento(self, event=None):
        """Atualiza o placeholder do campo documento baseado no tipo."""
        # Funcionalidade futura
        pass
    
    def salvar(self):
        """Salva o parceiro."""
        # Coleta dados
        dados = {
            'nome': capitalizar_nome(self.entrada_nome.get().strip()),
            'tipo_documento': self.combo_tipo_doc.get(),
            'documento': remover_formatacao(self.entrada_documento.get()),
            'email': self.entrada_email.get().strip(),
            'telefone': remover_formatacao(self.entrada_telefone.get()),
            'endereco': self.entrada_endereco.get().strip(),
            'cidade': self.entrada_cidade.get().strip(),
            'estado': self.combo_estado.get().upper(),
            'cep': remover_formatacao(self.entrada_cep.get()),
            'tipo_parceiro': self.combo_tipo_parceiro.get(),
            'status': self.combo_status.get(),
            'observacoes': self.texto_obs.get('1.0', tk.END).strip()
        }
        
        # Salva
        if self.modo_edicao:
            sucesso, mensagem = self.controller.atualizar_parceiro(
                self.parceiro['id'],
                dados
            )
        else:
            sucesso, mensagem, _ = self.controller.criar_parceiro(dados)
        
        if sucesso:
            messagebox.showinfo("Sucesso", mensagem)
            self.janela.destroy()
            self.view_pai.atualizar_lista()
        else:
            messagebox.showerror("Erro", mensagem)