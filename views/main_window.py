#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Janela Principal
--------------
Implementa a janela principal da aplicação com todas as abas e funcionalidades.
"""
# main_window.py
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import logging
import datetime
import webbrowser

from views.parceiro_view import ParceiroView
from views.loja_view import LojaView
from views.comprovante_view import ComprovanteView
from views.associacao_view import AssociacaoView
from views.relatorio_view import RelatorioView
from views.config_view import ConfigView
from controllers.config_controller import ConfigController


class MainWindow:
    def __init__(self, root, db_manager, config):
        self.root = root
        self.db_manager = db_manager
        self.config = config
        self.config_controller = ConfigController()
        self.logger = logging.getLogger(__name__)
        self.root.title("Sistema de Gestão de Parceiros")

        self.configurar_estilo()
        self.criar_menu()
        self.criar_layout()

        # Exibir tela inicial
        self.trocar_view("Parceiros")

        self.root.update()
        self.root.minsize(self.root.winfo_width(), self.root.winfo_height())
        self.centralizar_janela()

    def configurar_estilo(self):
        style = ttk.Style()
        try:
            from ttkthemes import ThemedStyle
            style = ThemedStyle(self.root)
            style.set_theme("arc")
        except ImportError:
            self.logger.warning("ttkthemes não está instalado. Usando tema clam.")
            style.theme_use("clam")

        style.configure('TButton', padding=6)
        style.configure('TLabel', padding=3)
        style.configure('Treeview', rowheight=25)
        self.root.option_add("*Font", ("Segoe UI", 10))

    def criar_layout(self):
        self.container = ttk.Frame(self.root)
        self.container.pack(fill=tk.BOTH, expand=True)

        # Sidebar
        self.sidebar = ttk.Frame(self.container, width=180)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5), pady=5)

        self.botoes_sidebar = [
            ("Parceiros", lambda: self.trocar_view("Parceiros")),
            ("Lojas", lambda: self.trocar_view("Lojas")),
            ("Comprovantes", lambda: self.trocar_view("Comprovantes")),
            ("Associações", lambda: self.trocar_view("Associações")),
            ("Relatórios", lambda: self.trocar_view("Relatórios")),
        ]

        for texto, comando in self.botoes_sidebar:
            btn = ttk.Button(self.sidebar, text=texto, command=comando, width=20)
            btn.pack(pady=5, padx=10, anchor=tk.NW)

        # Área de conteúdo
        self.area_conteudo = ttk.Frame(self.container)
        self.area_conteudo.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Inicializar views
        self.views = {
            "Parceiros": ParceiroView(self.area_conteudo, self.db_manager),
            "Lojas": LojaView(self.area_conteudo, self.db_manager),
            "Comprovantes": ComprovanteView(self.area_conteudo, self.db_manager),
            "Associações": AssociacaoView(self.area_conteudo, self.db_manager),
            "Relatórios": RelatorioView(self.area_conteudo, self.db_manager),
        }

        for view in self.views.values():
            view.pack_forget()

    def trocar_view(self, nome_view):
        for nome, view in self.views.items():
            view.pack_forget()
        self.views[nome_view].pack(fill=tk.BOTH, expand=True)
        self.root.title(f"Sistema de Gestão - {nome_view}")
        self.logger.info(f"Aba alterada para: {nome_view}")

    def centralizar_janela(self):
        self.root.update_idletasks()
        largura_tela = self.root.winfo_screenwidth()
        altura_tela = self.root.winfo_screenheight()
        largura = self.root.winfo_width()
        altura = self.root.winfo_height()
        x = (largura_tela // 2) - (largura // 2)
        y = (altura_tela // 2) - (altura // 2)
        self.root.geometry(f"{largura}x{altura}+{x}+{y}")

    def criar_menu(self):
        """Cria o menu principal."""
        menu_bar = tk.Menu(self.root)

        # Menu Arquivo
        arquivo_menu = tk.Menu(menu_bar, tearoff=0)
        arquivo_menu.add_command(label="Backup do Banco de Dados", command=self.backup_database)
        arquivo_menu.add_command(label="Restaurar Backup", command=self.restore_database)
        arquivo_menu.add_separator()
        arquivo_menu.add_command(label="Sair", command=self.sair)
        menu_bar.add_cascade(label="Arquivo", menu=arquivo_menu)

        # Menu Cadastros
        cadastros_menu = tk.Menu(menu_bar, tearoff=0)
        cadastros_menu.add_command(label="Parceiros", command=lambda: self.notebook.select(0))
        cadastros_menu.add_command(label="Lojas", command=lambda: self.notebook.select(1))
        cadastros_menu.add_command(label="Comprovantes", command=lambda: self.notebook.select(2))
        cadastros_menu.add_command(label="Associações", command=lambda: self.notebook.select(3))
        menu_bar.add_cascade(label="Cadastros", menu=cadastros_menu)

        # Menu Relatórios
        relatorios_menu = tk.Menu(menu_bar, tearoff=0)
        relatorios_menu.add_command(label="Relatórios", command=lambda: self.notebook.select(4))
        relatorios_menu.add_separator()
        relatorios_menu.add_command(label="Entregas por Parceiro", command=self.relatorio_por_parceiro)
        relatorios_menu.add_command(label="Entregas por Loja", command=self.relatorio_por_loja)
        relatorios_menu.add_command(label="Entregas por Período", command=self.relatorio_por_periodo)
        menu_bar.add_cascade(label="Relatórios", menu=relatorios_menu)

        # Menu Configurações
        config_menu = tk.Menu(menu_bar, tearoff=0)
        config_menu.add_command(label="Preferências", command=self.abrir_configuracoes)
        menu_bar.add_cascade(label="Configurações", menu=config_menu)

        # Menu Ajuda
        ajuda_menu = tk.Menu(menu_bar, tearoff=0)
        ajuda_menu.add_command(label="Manual do Usuário", command=self.abrir_manual)
        ajuda_menu.add_command(label="Sobre", command=self.mostrar_sobre)
        menu_bar.add_cascade(label="Ajuda", menu=ajuda_menu)

        self.root.config(menu=menu_bar)

    def criar_notebook(self):
        """Cria o notebook (abas) para as diferentes seções."""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Inicializar as views
        self.parceiro_view = ParceiroView(self.notebook, self.db_manager)
        self.loja_view = LojaView(self.notebook, self.db_manager)
        self.comprovante_view = ComprovanteView(self.notebook, self.db_manager)
        self.associacao_view = AssociacaoView(self.notebook, self.db_manager)
        self.relatorio_view = RelatorioView(self.notebook, self.db_manager)

        # Adicionar as abas
        self.notebook.add(self.parceiro_view, text="Parceiros")
        self.notebook.add(self.loja_view, text="Lojas")
        self.notebook.add(self.comprovante_view, text="Comprovantes")
        self.notebook.add(self.associacao_view, text="Associações")
        self.notebook.add(self.relatorio_view, text="Relatórios")

        # Vincular evento de mudança de aba
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

    def configurar_atalhos(self):
        """Configura atalhos de teclado para a aplicação."""
        # Atalhos globais
        self.root.bind("<Control-b>", lambda e: self.backup_database())
        self.root.bind("<Control-r>", lambda e: self.restore_database())
        self.root.bind("<Control-q>", lambda e: self.sair())

        # Atalhos para navegação de abas
        self.root.bind("<Control-1>", lambda e: self.notebook.select(0))
        self.root.bind("<Control-2>", lambda e: self.notebook.select(1))
        self.root.bind("<Control-3>", lambda e: self.notebook.select(2))
        self.root.bind("<Control-4>", lambda e: self.notebook.select(3))
        self.root.bind("<Control-5>", lambda e: self.notebook.select(4))

        # Atalho para ajuda
        self.root.bind("<F1>", lambda e: self.abrir_manual())

    def on_tab_changed(self, event=None):
        """Manipula o evento de mudança de aba."""
        tab_index = self.notebook.index(self.notebook.select())
        tab_name = self.notebook.tab(tab_index, "text")
        self.logger.info(f"Aba alterada para '{tab_name}'")

        # Focar no campo principal da aba selecionada
        if tab_index == 0:  # Parceiros
            self.parceiro_view.focus_nome()
        elif tab_index == 1:  # Lojas
            self.loja_view.focus_nome()
        elif tab_index == 2:  # Comprovantes
            self.comprovante_view.focus_parceiro()
        elif tab_index == 3:  # Associações
            self.associacao_view.focus_parceiro()

    def backup_database(self):
        """Realiza backup do banco de dados."""
        try:
            # Definir diretório e nome do arquivo de backup
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"backup_gestao_parceiros_{timestamp}.db"

            filepath = filedialog.asksaveasfilename(
                title="Salvar Backup do Banco de Dados",
                initialfile=default_filename,
                defaultextension=".db",
                filetypes=[("Arquivos de Banco de Dados", "*.db"), ("Todos os Arquivos", "*.*")]
            )

            if not filepath:
                return  # Usuário cancelou

            # Realizar o backup
            backup_path = self.db_manager.backup_database(filepath)

            if backup_path:
                messagebox.showinfo(
                    "Backup Concluído",
                    f"Backup do banco de dados realizado com sucesso!\nArquivo: {backup_path}"
                )
                self.logger.info(f"Backup realizado: {backup_path}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao realizar backup: {str(e)}")
            self.logger.error(f"Erro ao realizar backup: {str(e)}")

    def restore_database(self):
        """Restaura o banco de dados a partir de um backup."""
        try:
            # Confirmar restauração
            confirmacao = messagebox.askyesno(
                "Confirmar Restauração",
                "A restauração substituirá todos os dados atuais pelos dados do backup.\n"
                "Deseja continuar? Recomenda-se fazer um backup antes de prosseguir."
            )

            if not confirmacao:
                return

            # Selecionar arquivo de backup
            filepath = filedialog.askopenfilename(
                title="Selecionar Arquivo de Backup",
                filetypes=[("Arquivos de Banco de Dados", "*.db"), ("Todos os Arquivos", "*.*")]
            )

            if not filepath:
                return  # Usuário cancelou

            # Realizar a restauração
            success = self.db_manager.restore_database(filepath)

            if success:
                messagebox.showinfo(
                    "Restauração Concluída",
                    "Banco de dados restaurado com sucesso!\nA aplicação será reiniciada."
                )
                self.logger.info(f"Banco de dados restaurado de: {filepath}")

                # Reiniciar aplicação para carregar os dados restaurados
                self.reiniciar_aplicacao()
            else:
                messagebox.showerror(
                    "Erro",
                    "Falha na restauração do banco de dados.\nVerifique o arquivo de backup."
                )

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao restaurar backup: {str(e)}")
            self.logger.error(f"Erro ao restaurar backup: {str(e)}")

    def reiniciar_aplicacao(self):
        """Reinicia a aplicação após restauração do banco de dados."""
        # Limpar e recarregar os dados nas interfaces
        try:
            # Recarregar os dados nas views
            self.parceiro_view._carregar_parceiros()
            self.loja_view._carregar_lojas()
            self.comprovante_view._carregar_comprovantes()
            self.associacao_view._carregar_associacoes()

            # Limpar campos
            self.parceiro_view._limpar_form()
            self.loja_view._limpar_form()
            self.comprovante_view._limpar_form()
            self.associacao_view._limpar_form()

            self.logger.info("Dados recarregados após restauração")
        except Exception as e:
            self.logger.error(f"Erro ao recarregar dados: {str(e)}")
            # Em caso de erro grave, sugerir reiniciar o aplicativo
            messagebox.showwarning(
                "Reinicialização Necessária",
                "Recomenda-se fechar e abrir novamente o aplicativo para carregar corretamente os dados restaurados."
            )

    def relatorio_por_parceiro(self):
        """Abre a aba de relatórios e configura para mostrar relatório por parceiro."""
        self.notebook.select(4)  # Seleciona a aba de relatórios
        self.relatorio_view.selecionar_tipo("parceiro")

    def relatorio_por_loja(self):
        """Abre a aba de relatórios e configura para mostrar relatório por loja."""
        self.notebook.select(4)  # Seleciona a aba de relatórios
        self.relatorio_view.selecionar_tipo("loja")

    def relatorio_por_periodo(self):
        """Abre a aba de relatórios e configura para mostrar relatório por período."""
        self.notebook.select(4)  # Seleciona a aba de relatórios
        self.relatorio_view.selecionar_tipo("periodo")

    def abrir_configuracoes(self):
        """Abre a janela de configurações do sistema."""
        ConfigView(self.root, self.config_controller)

    def abrir_manual(self):
        """Abre o manual do usuário."""
        manual_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                   "resources", "manual_usuario.pdf")

        if os.path.exists(manual_path):
            # Abrir com o visualizador padrão do sistema
            try:
                webbrowser.open(manual_path)
                self.logger.info(f"Manual do usuário aberto: {manual_path}")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao abrir manual: {str(e)}")
                self.logger.error(f"Erro ao abrir manual: {str(e)}")
        else:
            messagebox.showinfo(
                "Manual do Usuário",
                "O manual do usuário não está disponível.\n"
                "Por favor, consulte a documentação online ou entre em contato com o suporte."
            )
            self.logger.warning(f"Manual do usuário não encontrado: {manual_path}")

    def mostrar_sobre(self):
        """Mostra informações sobre o sistema."""
        # Criação da janela 'Sobre'
        sobre_window = tk.Toplevel(self.root)
        sobre_window.title("Sobre o Sistema")
        sobre_window.geometry("500x300")
        sobre_window.resizable(False, False)
        sobre_window.transient(self.root)  # Janela sempre na frente da principal
        sobre_window.grab_set()  # Torna a janela modal

        # Centralizar na janela principal
        sobre_window.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (sobre_window.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (sobre_window.winfo_height() // 2)
        sobre_window.geometry(f"+{x}+{y}")

        # Conteúdo
        frame = ttk.Frame(sobre_window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        # Título
        ttk.Label(frame, text="Sistema de Gestão de Parceiro",
                  font=("Segoe UI", 16, "bold")).pack(pady=(0, 10))

        # Versão
        ttk.Label(frame, text="Versão 1.0", font=("Segoe UI", 10)).pack(pady=(0, 20))

        # Descrição
        descricao = (
            "Um sistema para gerenciamento de parceiros, lojas atendidas, "
            "comprovantes de entregas e geração de relatórios."
        )
        ttk.Label(frame, text=descricao, wraplength=450, justify="center").pack(pady=(0, 20))

        # Direitos autorais
        ttk.Label(frame, text=f"© {datetime.datetime.now().year} - Todos os direitos reservados",
                  font=("Segoe UI", 9)).pack(pady=(20, 0))

        # Botão fechar
        ttk.Button(frame, text="Fechar", command=sobre_window.destroy).pack(pady=(20, 0))

    def centralizar_janela(self):
        """Centraliza a janela principal na tela."""
        # Atualizar a janela para garantir que as dimensões estejam corretas
        self.root.update_idletasks()

        # Obter dimensões da tela
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Obter dimensões da janela
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()

        # Calcular posição
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)

        # Definir geometria
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    def sair(self):
        """Fecha a aplicação."""
        if messagebox.askyesno("Sair", "Deseja realmente sair do sistema?"):
            self.logger.info("Aplicação encerrada pelo usuário")
            self.root.quit()