import json
import os
import tkinter as tk
from tkinter import ttk

#Importa le funzioni che creano i tre tab e le funzioni del tema

from tabs_pomodoro import create_pomodoro_frame
from tabs_schedule import create_schedule_tab
from tabs_exams import create_exams_tab
from theme import apply_theme, set_dark_mode

THEME_PREF_FILE = "theme_pref.json"


def _load_theme_preference() -> bool:
    #Restituisce True se l'ultima preferenza salva il tema scuro altrimenti se il file non esiste o è light restituisce False
    # Tengo la logica semplice: se qualcosa va storto ricado nel tema chiaro e l'utente non rimane senza interfaccia
    if not os.path.exists(THEME_PREF_FILE):
        return False
    try:
        with open(THEME_PREF_FILE, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        return bool(data.get("dark", False))
    except Exception:
        # Non mi interessa il motivo preciso, qui voglio solo evitare di alzare eccezioni durante l'avvio
        return False


def _save_theme_preference(enabled: bool) -> None:
    #salva le preferenze del tema
    try:
        with open(THEME_PREF_FILE, "w", encoding="utf-8") as fh:
            json.dump({"dark": bool(enabled)}, fh, indent=2)
    except Exception:
        # Se fallisce il salvataggio non blocchiamo l'app
        pass


def _build_header(root: tk.Tk, parent: ttk.Frame, theme_var: tk.BooleanVar) -> None: #header è un contenitore "card"
    header = ttk.Frame(parent, style="Surface.TFrame", padding=(16, 14))
    header.pack(fill="x", pady=(0, 16))
    header.columnconfigure(0, weight=1)

    #Gestisce la parte grafica della finestra come tutto cio che sta fuori dalle finestre e le impostazioni del tema

    ttk.Label(header, text="Studio Planner", style="AppTitle.TLabel").grid(row=0, column=0, sticky="w")
    # Sotto il titolo aggiungo una descrizione breve così l'app risulta meno "spoglia" al primo avvio
    ttk.Label(
        header,
        text="Timer, orari e progressi in un'unica interfaccia.",
        style="SurfaceSubtle.TLabel",
    ).grid(row=1, column=0, sticky="w", pady=(6, 0))

    def _on_toggle():
        set_dark_mode(root, theme_var.get())
        _save_theme_preference(theme_var.get())
        root.event_generate("<<PlannerThemeChanged>>")

    theme_switch = ttk.Checkbutton(
        header,
        text="Tema scuro",
        variable=theme_var,
        command=_on_toggle,
        style="Switch.TCheckbutton",
    )
    theme_switch.grid(row=0, column=1, rowspan=2, sticky="e")


def main(): #avvia il programma
    root = tk.Tk() #crea la finestra grafica
    root.title("Studio Planner") #titolo
    root.minsize(860, 620) #dimensione minima

    dark_enabled = _load_theme_preference() 
    apply_theme(root, "dark" if dark_enabled else "light") #applica preferenza temi

    container = ttk.Frame(root, style="Background.TFrame", padding=20)
    container.pack(fill="both", expand=True)

    theme_var = tk.BooleanVar(value=dark_enabled) #crea un container di sfondo che ha il titolo e la preferenza del tema
    # Mi salvo la preferenza del tema dentro una variabile Tk in modo da sincronizzare facilmente il toggle con il resto della GUI
    _build_header(root, container, theme_var)

    notebook_card = ttk.Frame(container, style="Surface.TFrame", padding=16) #crea una card per ospitare il notebook (schede)
    notebook_card.pack(fill="both", expand=True)

    notebook = ttk.Notebook(notebook_card, style="Planner.TNotebook")
    notebook.pack(fill="both", expand=True) #instanzia notebook con stile personalizzato
    # Da qui in poi basta aggiungere tab al notebook: l'ordine delle add determina la posizione delle schede

    #inseriamo le 3 schede
    
    pomodoro_tab = create_pomodoro_frame(notebook)
    notebook.add(pomodoro_tab, text="Pomodoro")
    # Ogni tab è costruita in un modulo separato: qui mi limito a montarla nel notebook

    schedule_tab = create_schedule_tab(notebook)
    notebook.add(schedule_tab, text="Orario di oggi")

    exams_tab = create_exams_tab(notebook)
    notebook.add(exams_tab, text="Esami")

    # Chiudo con il classico loop Tk: da qui l'app vive degli eventi generati dall'utente
    root.mainloop()


if __name__ == "__main__": #avvio dell’app GUI quando lancio tabs_app.py
    main()
