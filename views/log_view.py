from tkinter import ttk
from utils.logger import LogManager
import tkinter as tk

class LogView(ttk.Frame):
    """Visualizador de logs da aplicação."""

    def __init__(self, parent, log_dir):
        super().__init__(parent)
        self.log_dir = log_dir
        self.log_files = []
        self._criar_widgets()
        self._carregar_logs()

    def _criar_widgets(self):
        left = ttk.Frame(self)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        self.listbox = tk.Listbox(left, width=30)
        self.listbox.pack(fill=tk.BOTH, expand=True)
        self.listbox.bind('<<ListboxSelect>>', self._mostrar_log)

        right = ttk.Frame(self)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        search_frame = ttk.Frame(right)
        search_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(search_frame, text="Buscar:").pack(side=tk.LEFT)
        self.entry_search = ttk.Entry(search_frame, width=30)
        self.entry_search.pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Ir", command=self._buscar_texto).pack(side=tk.LEFT)
        self.entry_search.bind("<Return>", lambda _e: self._buscar_texto())

        self.text = tk.Text(right, wrap='none')
        self.text.pack(fill=tk.BOTH, expand=True)

    def _carregar_logs(self):
        self.log_files = LogManager.list_log_files(self.log_dir)
        self.listbox.delete(0, tk.END)
        for nome in self.log_files:
            self.listbox.insert(tk.END, nome)

    def _mostrar_log(self, _event=None):
        if not self.listbox.curselection():
            return
        index = self.listbox.curselection()[0]
        log_name = self.log_files[index]
        conteudo = LogManager.read_log_file(self.log_dir, log_name)
        self.text.delete('1.0', tk.END)
        self.text.insert('1.0', conteudo)

    def _buscar_texto(self):
        """Realiza busca no texto do log e destaca as ocorrências."""
        termo = self.entry_search.get().strip()
        self.text.tag_remove('highlight', '1.0', tk.END)
        if not termo:
            return
        idx = '1.0'
        while True:
            idx = self.text.search(termo, idx, nocase=True, stopindex=tk.END)
            if not idx:
                break
            end_idx = f"{idx}+{len(termo)}c"
            self.text.tag_add('highlight', idx, end_idx)
            idx = end_idx
        self.text.tag_config('highlight', background='yellow')