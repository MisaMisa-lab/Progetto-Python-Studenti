from tkinter import ttk
from types import SimpleNamespace


LIGHT = {
    "bg": "#FEFEFF",
    "surface": "#FFFFFF",
    "surface_soft": "#F7F8FF",
    "text": "#2E3532",
    "text2": "#6F7674",
    "primary": "#5465FF",
    "primary_hover": "#4351E8",
    "border": "#E4E7F5",
    "table_alt": "#F4F6FF",
}

DARK = {
    "bg": "#0B1220",
    "surface": "#0F172A",
    "surface_soft": "#111827",
    "text": "#E5E7EB",
    "text2": "#9CA3AF",
    "primary": "#818CF8",
    "primary_hover": "#A5B4FC",
    "border": "#263449",
    "table_alt": "#141C2E",
}


def apply_theme(root, mode: str = "light"):
    colors = LIGHT if mode == "light" else DARK
    root.configure(bg=colors["bg"])

    style = ttk.Style(root)

    try:
        style.theme_use("clam")
    except Exception:
        pass

    apply_styles(style, colors)

    root._APP_THEME = mode
    root._planner_palette = SimpleNamespace(
        base=colors["bg"],
        surface=colors["surface"],
        soft_surface=colors["surface_soft"],
        border=colors["border"],
        accent=colors["primary"],
        alternate=colors["table_alt"],
        text=colors["text"],
        muted=colors["text2"],
    )


def set_dark_mode(root, enabled: bool):
    apply_theme(root, "dark" if enabled else "light")


def apply_styles(style: ttk.Style, c: dict):
    font_text = ("Inter", 10)
    font_button = ("Inter", 10)
    font_title = ("Poppins", 18, "bold")
    font_value = ("Inter", 12, "bold")

    style.configure("TFrame", background=c["bg"])
    style.configure("Background.TFrame", background=c["bg"])
    style.configure("Surface.TFrame", background=c["surface"])
    style.configure("SoftSurface.TFrame", background=c["surface_soft"])
    style.configure("Header.TFrame", background=c["surface"])

    style.configure("TLabel", background=c["bg"], foreground=c["text"], font=font_text)
    style.configure("Subtle.TLabel", background=c["bg"], foreground=c["text2"], font=font_text)
    style.configure("Surface.TLabel", background=c["surface"], foreground=c["text"], font=font_text)
    style.configure("SurfaceSubtle.TLabel", background=c["surface"], foreground=c["text2"], font=font_text)
    style.configure("SoftSurfaceSubtle.TLabel", background=c["surface_soft"], foreground=c["text2"], font=font_text)

    style.configure("AppTitle.TLabel", background=c["surface"], foreground=c["text"], font=font_title)
    style.configure("AppSubtitle.TLabel", background=c["surface"], foreground=c["text2"], font=font_text)
    style.configure("Value.TLabel", background=c["surface"], foreground=c["primary"], font=font_value)

    style.configure(
        "TButton",
        background=c["surface_soft"],
        foreground=c["text"],
        bordercolor=c["border"],
        padding=(10, 5),
        font=font_button,
        relief="flat",
    )
    style.map("TButton", background=[("active", c["table_alt"])])

    style.configure(
        "Primary.TButton",
        background=c["primary"],
        foreground="#FFFFFF",
        bordercolor=c["primary"],
        padding=(12, 6),
        font=font_button,
        relief="flat",
    )
    style.map("Primary.TButton", background=[("active", c["primary_hover"])])

    style.configure(
        "Switch.TCheckbutton",
        background=c["surface_soft"],
        foreground=c["text"],
        padding=(12, 5),
        font=font_button,
        indicatoron=False,
        relief="flat",
    )
    style.map(
        "Switch.TCheckbutton",
        background=[("selected", c["primary"]), ("active", c["table_alt"])],
        foreground=[("selected", "#FFFFFF")],
    )

    style.configure(
        "Surface.TCheckbutton",
        background=c["surface"],
        foreground=c["text"],
        padding=(4, 3),
        font=font_text,
    )

    style.configure("Planner.TNotebook", background=c["surface"], borderwidth=0, padding=4)
    style.configure("TNotebook", background=c["surface"], borderwidth=0)
    style.configure(
        "TNotebook.Tab",
        background=c["surface"],
        foreground=c["text2"],
        padding=(14, 7),
        font=("Inter", 10),
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", c["surface_soft"]), ("active", c["table_alt"])],
        foreground=[("selected", c["primary"]), ("active", c["text"])],
    )

    for widget in ("TEntry", "TSpinbox", "TCombobox", "Planner.TCombobox"):
        style.configure(
            widget,
            fieldbackground=c["surface"],
            background=c["surface"],
            foreground=c["text"],
            bordercolor=c["border"],
            insertcolor=c["text"],
            arrowcolor=c["text"],
            padding=(7, 5),
            font=font_text,
        )
        style.map(widget, fieldbackground=[("readonly", c["surface"])])

    style.configure(
        "Surface.TLabelframe",
        background=c["surface"],
        bordercolor=c["border"],
        relief="solid",
        borderwidth=1,
        padding=(10, 8),
    )
    style.configure(
        "Surface.TLabelframe.Label",
        background=c["surface"],
        foreground=c["text"],
        font=("Poppins", 10, "bold"),
    )

    style.configure(
        "Treeview",
        background=c["surface"],
        fieldbackground=c["surface"],
        foreground=c["text"],
        rowheight=27,
        font=font_text,
        bordercolor=c["border"],
    )
    style.configure(
        "Treeview.Heading",
        background=c["surface_soft"],
        foreground=c["text"],
        padding=(7, 5),
        font=("Inter", 10, "bold"),
        relief="flat",
    )
    style.map(
        "Treeview",
        background=[("selected", c["primary"])],
        foreground=[("selected", "#FFFFFF")],
    )