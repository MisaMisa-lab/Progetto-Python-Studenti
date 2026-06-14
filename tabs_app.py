import json
import os
import tkinter as tk
from tkinter import ttk

from tabs_pomodoro import create_pomodoro_frame
from tabs_schedule import create_schedule_tab
from tabs_exams import create_exams_tab
from theme import apply_theme, set_dark_mode

THEME_PREF_FILE = "theme_pref.json"


def load_theme_preference() -> bool:
    if not os.path.exists(THEME_PREF_FILE):
        return False

    try:
        with open(THEME_PREF_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
        return bool(data.get("dark", False))
    except Exception:
        return False


def save_theme_preference(enabled: bool):
    try:
        with open(THEME_PREF_FILE, "w", encoding="utf-8") as file:
            json.dump({"dark": enabled}, file, indent=2)
    except Exception:
        pass


def setup_window(root: tk.Tk):
    root.title("Studify")
    root.minsize(940, 600)

    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()

    width = max(940, min(1120, screen_w - 120))
    height = max(600, min(720, screen_h - 120))

    x = max(0, (screen_w - width) // 2)
    y = max(0, (screen_h - height) // 2 - 10)

    root.geometry(f"{width}x{height}+{x}+{y}")


def build_header(root: tk.Tk, parent: ttk.Frame, theme_var: tk.BooleanVar):
    header = ttk.Frame(parent, style="Header.TFrame", padding=(16, 10))
    header.pack(fill="x", pady=(0, 10))
    header.columnconfigure(0, weight=1)

    ttk.Label(header, text="Studify", style="AppTitle.TLabel").grid(row=0, column=0, sticky="w")
    ttk.Label(
        header,
        text="Turn procrastination into progress",
        style="AppSubtitle.TLabel",
    ).grid(row=1, column=0, sticky="w", pady=(2, 0))

    def toggle_theme():
        set_dark_mode(root, theme_var.get())
        save_theme_preference(theme_var.get())
        root.event_generate("<<PlannerThemeChanged>>")

    ttk.Checkbutton(
        header,
        text="Tema scuro",
        variable=theme_var,
        command=toggle_theme,
        style="Switch.TCheckbutton",
    ).grid(row=0, column=1, rowspan=2, sticky="e")


def main():
    root = tk.Tk()
    setup_window(root)

    dark_enabled = load_theme_preference()
    apply_theme(root, "dark" if dark_enabled else "light")

    container = ttk.Frame(root, style="Background.TFrame", padding=14)
    container.pack(fill="both", expand=True)

    theme_var = tk.BooleanVar(value=dark_enabled)
    build_header(root, container, theme_var)

    notebook_card = ttk.Frame(container, style="Surface.TFrame", padding=(10, 8, 10, 10))
    notebook_card.pack(fill="both", expand=True)

    notebook = ttk.Notebook(notebook_card, style="Planner.TNotebook")
    notebook.pack(fill="both", expand=True)

    notebook.add(create_pomodoro_frame(notebook), text="Pomodoro")
    notebook.add(create_schedule_tab(notebook), text="Orario di oggi")
    notebook.add(create_exams_tab(notebook), text="Esami")

    root.mainloop()


if __name__ == "__main__":
    main()