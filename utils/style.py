from tkinter import ttk

_styles_applied = False


def configurar_estilos_modernos():
    """Aplica estilos modernos utilizados pelas interfaces."""
    global _styles_applied
    if _styles_applied:
        return

    style = ttk.Style()

    # Estilo para botões principais
    style.configure("Primary.TButton",
                    font=("Segoe UI", 10, "bold"),
                    padding=(10, 5))

    # Estilo para botões de ação
    style.configure("Action.TButton",
                    font=("Segoe UI", 9),
                    padding=(8, 4))

    # Estilo para botões de perigo
    style.configure("Danger.TButton",
                    font=("Segoe UI", 9),
                    padding=(8, 4))

    # Estilo para campos de entrada
    style.configure("Modern.TEntry",
                    fieldbackground="white",
                    borderwidth=1,
                    relief="solid",
                    padding=(5, 3))

    # Estilo para labels
    style.configure("Bold.TLabel",
                    font=("Segoe UI", 10, "bold"))

    # Estilo para frames
    style.configure("Card.TLabelframe",
                    relief="groove",
                    borderwidth=1,
                    padding=(10, 10))

    # Estilo para Treeview
    style.configure("Modern.Treeview",
                    background="white",
                    foreground="black",
                    rowheight=28,
                    fieldbackground="white",
                    font=("Segoe UI", 10))

    style.configure("Modern.Treeview.Heading",
                    font=("Segoe UI", 10, "bold"),
                    background="#f0f0f0",
                    foreground="black")

    # Cores para linhas alternadas
    style.map("Modern.Treeview",
              background=[("selected", "#0078d4")],
              foreground=[("selected", "white")])

    _styles_applied = True
