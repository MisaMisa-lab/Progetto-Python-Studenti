import json
import os
import sys
import tkinter as tk
from tkinter import ttk

from tabs_pomodoro import create_pomodoro_frame
from tabs_schedule import create_schedule_tab
from tabs_exams import create_exams_tab
from theme import apply_theme, set_dark_mode

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

HEADER_LOGO_SIZE = 110
WINDOW_LOGO_SIZE = 64


def get_app_dir() -> str:
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)

    return BASE_DIR


def get_resource_path(*parts: str) -> str:
    relative_path = os.path.join(*parts)

    possible_paths = []

    if hasattr(sys, "_MEIPASS"):
        possible_paths.append(os.path.join(sys._MEIPASS, relative_path))

    possible_paths.append(os.path.join(get_app_dir(), relative_path))
    possible_paths.append(os.path.join(BASE_DIR, relative_path))

    for path in possible_paths:
        if os.path.exists(path):
            return path

    return possible_paths[0]


def get_data_path(file_name: str) -> str:
    return os.path.join(get_app_dir(), file_name)


THEME_PREF_FILE = get_data_path("theme_pref.json")

LOGO_LIGHT_FILE = get_resource_path("img", "logo_light.png")
LOGO_DARK_FILE = get_resource_path("img", "logo_dark.png")
LOGO_ICON_FILE = get_resource_path("img", "logo.ico")


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


def load_image(path: str, max_size: int | None = None, enlarge: bool = False):
    if not os.path.exists(path):
        return None

    try:
        image = tk.PhotoImage(file=path)

        if max_size is not None:
            bigger_side = max(image.width(), image.height())

            if bigger_side > max_size:
                factor = (bigger_side + max_size - 1) // max_size
                image = image.subsample(factor, factor)

            elif enlarge and bigger_side < max_size * 0.85:
                factor = max(2, round(max_size / bigger_side))
                image = image.zoom(factor, factor)

        return image

    except tk.TclError:
        return None


class StudifyApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.dark_enabled = load_theme_preference()

        self.logo_image = None
        self.logo_label = None
        self.window_icon = None

        self.setup_window()
        self.setup_icon()

        apply_theme(self, "dark" if self.dark_enabled else "light")

        self.build_layout()

    def setup_window(self):
        self.title("Studify")
        self.minsize(940, 600)

        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()

        width = max(940, min(1120, screen_w - 120))
        height = max(600, min(720, screen_h - 120))

        x = max(0, (screen_w - width) // 2)
        y = max(0, (screen_h - height) // 2 - 10)

        self.geometry(f"{width}x{height}+{x}+{y}")

    def setup_icon(self):
        if os.path.exists(LOGO_ICON_FILE):
            try:
                self.iconbitmap(LOGO_ICON_FILE)
                return
            except tk.TclError:
                pass

        self.window_icon = load_image(LOGO_DARK_FILE, max_size=WINDOW_LOGO_SIZE)

        if self.window_icon is not None:
            try:
                self.iconphoto(True, self.window_icon)
            except tk.TclError:
                pass

    def build_layout(self):
        self.container = ttk.Frame(self, style="Background.TFrame", padding=14)
        self.container.pack(fill="both", expand=True)

        self.theme_var = tk.BooleanVar(value=self.dark_enabled)

        self.build_header()
        self.build_tabs()

    def build_header(self):
        header = ttk.Frame(self.container, style="Header.TFrame", padding=(16, 10))
        header.pack(fill="x", pady=(0, 10))

        header.columnconfigure(1, weight=1)

        self.logo_label = ttk.Label(header, style="Surface.TLabel")
        self.logo_label.grid(row=0, column=0, rowspan=2, sticky="w", padx=(0, 14))

        self.update_header_logo()

        title_area = ttk.Frame(header, style="Header.TFrame")
        title_area.grid(row=0, column=1, rowspan=2, sticky="w")

        ttk.Label(
            title_area,
            text="Studify",
            style="AppTitle.TLabel",
        ).grid(row=0, column=0, sticky="w")

        ttk.Label(
            title_area,
            text="Turn procrastination into progress",
            style="AppSubtitle.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(2, 0))

        ttk.Checkbutton(
            header,
            text="Tema scuro",
            variable=self.theme_var,
            command=self.toggle_theme,
            style="Switch.TCheckbutton",
        ).grid(row=0, column=2, rowspan=2, sticky="e")

    def build_tabs(self):
        notebook_card = ttk.Frame(
            self.container,
            style="Surface.TFrame",
            padding=(10, 8, 10, 10),
        )
        notebook_card.pack(fill="both", expand=True)

        notebook = ttk.Notebook(notebook_card, style="Planner.TNotebook")
        notebook.pack(fill="both", expand=True)

        notebook.add(create_pomodoro_frame(notebook), text="Pomodoro")
        notebook.add(create_schedule_tab(notebook), text="Orario di oggi")
        notebook.add(create_exams_tab(notebook), text="Esami")

    def toggle_theme(self):
        enabled = self.theme_var.get()

        set_dark_mode(self, enabled)
        save_theme_preference(enabled)

        self.update_header_logo()
        self.event_generate("<<PlannerThemeChanged>>")

    def update_header_logo(self):
        if self.theme_var.get():
            logo_file = LOGO_DARK_FILE
        else:
            logo_file = LOGO_LIGHT_FILE

        self.logo_image = load_image(
            logo_file,
            max_size=HEADER_LOGO_SIZE,
            enlarge=True,
        )

        if self.logo_image is None:
            self.logo_label.configure(image="", text="")
            return

        self.logo_label.configure(image=self.logo_image, text="")


def main():
    app = StudifyApp()
    app.mainloop()


if __name__ == "__main__":
    main()