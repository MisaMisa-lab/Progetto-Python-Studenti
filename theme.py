# theme.py
from tkinter import ttk
from types import SimpleNamespace 

#Tema Light

_LIGHT = { 
    "bg": "#F8FAFC",            # finestra background
    "surface": "#FFFFFF",       # sfondo card / contenitori
    "text": "#0F172A",          # testo principale
    "text2": "#475569",         # testo secondario
    "primary": "#4F46E5",       # bottoni
    "primary_hover": "#4338CA", #evidenzia elementi attivi al passaggio del mouse
    "border": "#C7D2FE",        #colore dei bordi
    "focus": "#93C5FD",         #focus inserimento da tastiera
    "table_bg": "#FFFFFF",      #colore righe tabella
    "table_alt": "#EEF2FF",     #colore alternativo righe tabella
}

#Tema Dark

_DARK = {
    "bg": "#0B1220",
    "surface": "#0F172A",
    "text": "#E5E7EB",
    "text2": "#9CA3AF",
    "primary": "#818CF8",
    "primary_hover": "#A5B4FC",
    "border": "#334155",
    "focus": "#3B82F6",
    "table_bg": "#0F172A",
    "table_alt": "#141C2E",
}

def _apply_common(style: ttk.Style, C: dict): #Applica gli stili base usando i colori correnti (palette C)
    # Frame + Label
    style.configure("TFrame", background=C["bg"]) #sfondo generale della finestra
    style.configure("Background.TFrame", background=C["bg"])  #sfondo generale della finestra.
    style.configure("Surface.TFrame", background=C["surface"]) #contenitore con sfondo surface
    #card con testo principale o secondario
    style.configure("TLabel", background=C["bg"], foreground=C["text"])
    style.configure("Subtle.TLabel", background=C["bg"], foreground=C["text2"])
    style.configure("SurfaceSubtle.TLabel", background=C["surface"], foreground=C["text2"])
    style.configure("Surface.TLabel", background=C["surface"], foreground=C["text"])

    style.configure("AppTitle.TLabel", background=C["surface"], foreground=C["text"], font=("Helvetica", 20, "bold")) #stile titolo grosso

    # Separator
    style.configure("TSeparator", background=C["border"]) #Separatore usa il colore del bordo

    # Buttons
    style.configure( #Serve a impostare l’aspetto di base di un widget
        "TButton", #tutti i bottoni standard avranno queste proprietà
        background=C["surface"], #il bottone appare dello stesso colore dei pannelli
        foreground=C["text"], #il testo del bottone è scuro (light mode) o chiaro (dark mode)
        bordercolor=C["border"], #contorno leggero
        focusthickness=2, #Quando il bottone ha il focus, il bordo di focus è spesso 2 pixel
        focuscolor=C["focus"], #evidenzia bene il bottone attivo
        padding=(12, 6), #Spaziatura interna: 12 pixel orizzontali e 6 verticali
    )
    style.map( #mappa stati → proprietà
        "TButton", #comportamento dinamico dei bottoni (TButton)
        background=[("active", C["table_alt"])], #effetto hover: cambia colore quando ci passi sopra
        relief=[("pressed", "sunken")], #effetto pressione realistica
    )

    style.configure(
        "Primary.TButton",
        background=C["primary"],
        foreground="#FFFFFF",
        bordercolor=C["primary"],
        focusthickness=2,
        focuscolor=C["focus"],
        padding=(14, 8),
    )
    style.map(
        "Primary.TButton",
        background=[("active", C["primary_hover"])],
        bordercolor=[("active", C["primary_hover"])],
    )

    # Toggle
    style.configure( 
        "Switch.TCheckbutton", 
        background=C["surface"], 
        foreground=C["text"],
        bordercolor=C["border"],
        focusthickness=2,
        focuscolor=C["focus"],
        padding=(14, 6),
        indicatoron=False, #tutto il bottone fa da interruttore (niente casellina)
    )
    style.map(
        "Switch.TCheckbutton",
        background=[("selected", C["primary"]), ("active", C["table_alt"])],
        foreground=[("selected", "#FFFFFF")],
        bordercolor=[("selected", C["primary"]), ("active", C["focus"])],
    )

    style.configure(
        "Surface.TCheckbutton",
        background=C["surface"],
        foreground=C["text"],
        focusthickness=2,
        focuscolor=C["focus"],
        bordercolor=C["border"],
        indicatorcolor=C["border"],
        padding=(6, 4),
    )
    style.map(
        "Surface.TCheckbutton",
        background=[("active", C["table_alt"])],
        indicatorcolor=[("selected", C["primary"])],
        foreground=[("disabled", C["text2"])],
    )

    # Notebook (le schede)
    style.configure("Planner.TNotebook", background=C["surface"], borderwidth=0, padding=6)
    style.configure( #Stile delle singole tab
        "TNotebook.Tab",
        background=C["surface"],
        foreground=C["text"],
        padding=(16, 10),
    )
    style.map( #La tab selezionata evidenziata con table_alt
        "TNotebook.Tab",
        background=[("selected", C["table_alt"])],
        foreground=[("selected", C["text"])],
    )

    # Entry / Spinbox / Combobox Applica le stesse regole a questi tre input
    for w in ("TEntry", "TSpinbox", "Planner.TCombobox"):
        style.configure(
            w,
            fieldbackground=C["surface"],
            background=C["surface"],
            foreground=C["text"],
            bordercolor=C["border"],
            lightcolor=C["border"],
            darkcolor=C["border"],
            insertcolor=C["text"],
            arrowcolor=C["text"],
        )
        style.map(
            w,
            bordercolor=[("focus", C["focus"])],
            lightcolor=[("focus", C["focus"])],
            darkcolor=[("focus", C["focus"])],
            fieldbackground=[("readonly", C["surface"])],
        )

    # LabelFrame come card
    style.configure(
        "Surface.TLabelframe",
        background=C["surface"],
        bordercolor=C["border"],
        relief="solid",
        borderwidth=1,
        padding=(12, 10),
    )
    style.configure(
        "Surface.TLabelframe.Label",
        background=C["surface"],
        foreground=C["text2"],
        font=("Helvetica", 10, "bold"),
    )

    # Progressbar
    style.configure("TProgressbar", background=C["primary"], troughcolor=C["surface"], bordercolor=C["surface"])

    # Treeview
    style.configure(
        "Treeview",
        background=C["table_bg"],
        fieldbackground=C["table_bg"],
        foreground=C["text"],
        bordercolor=C["border"],
        rowheight=28,
    )
    style.configure(
        "Treeview.Heading",
        background=C["surface"],
        foreground=C["text"],
        relief="flat",
        padding=(8, 6),
        font=("Helvetica", 10, "bold"),
    )
    style.map(
        "Treeview.Heading",
        background=[("active", C["table_alt"]), ("pressed", C["primary"])],
        foreground=[("active", C["text"]), ("pressed", "#FFFFFF")],
    )
    style.map("Treeview", background=[("selected", C["focus"])], foreground=[("selected", "#FFFFFF")])

def apply_theme(root, mode: str = "light"):
    
    # Applica il tema a tutta l'app. mode: "light" | "dark"
    C = _LIGHT if mode == "light" else _DARK
    root.configure(bg=C["bg"])
    style = ttk.Style(root)
    # 'clam' permette di controllare colori/bordi meglio su ttk
    try:
        style.theme_use("clam")
    except Exception:
        pass
    _apply_common(style, C)

    # Memorizza la modalità sull'oggetto root per toggle futuri
    root._APP_THEME = mode
    root._planner_palette = SimpleNamespace(
        background=C["surface"],
        surface=C["surface"],
        base=C["bg"],
        border=C["border"],
        accent=C["primary"],
        alternate=C["table_alt"],
        text=C["text"],
    )

def set_dark_mode(root, enabled: bool):
    
    #Abilita/Disabilita dark mode e riapplica i colori.
    mode = "dark" if enabled else "light"
    apply_theme(root, mode)
    # Forza refresh dei widget esistenti (es. Treeview header)
    for w in root.winfo_children():
        _refresh_styles_recursive(w)

def _refresh_styles_recursive(widget):
    # Ricorsione leggera per aggiornare bg/surface sui Frame
    import tkinter as tk
    if isinstance(widget, (tk.Frame,)):
        try:
            # se è un "Surface.TFrame" lascia surface, altrimenti bg
            if str(widget.cget("class")) == "TFrame":
                widget.configure(bg=widget.master.cget("bg"))
        except Exception:
            pass
    for child in widget.winfo_children():
        _refresh_styles_recursive(child)
