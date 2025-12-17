import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from schedule_storage import load_schedule, save_schedule


class ScheduleTab(ttk.Frame):
    DAYS = ("Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato")

    def __init__(self, parent: tk.Widget): # Inizializza il Frame con padding e stile di sfondo personalizzato
        super().__init__(parent, padding=16, style="Background.TFrame")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)

        raw = load_schedule() # Carica il dizionario dal file JSON: {"Lunedì": [{time, subject, notes}, ...], ...}
        self.schedule = {day: list(raw.get(day, [])) for day in self.DAYS} # Crea sempre le chiavi per i giorni attesi anche se mancanti nel file

        today_index = datetime.now().weekday() # Trova l'indice del giorno corrente: datetime.weekday() restituisce 0=lunedì ... 6=domenica
        if 0 <= today_index < len(self.DAYS): # esclude la domenica (indice 6) non presente in DAYS
            self.current_day_index = today_index 
        else:
            self.current_day_index = 0 # fallback a Lunedì

        self._build_ui()
        self._refresh_day()
        self._apply_tree_styles()

        try: #tema
            self.winfo_toplevel().bind("<<PlannerThemeChanged>>", self._on_theme_change, add="+")
        except Exception:
            pass

    def _build_ui(self):
        header = ttk.Frame(self, style="Surface.TFrame", padding=(16, 14))
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)

        ttk.Label(header, text="Orario settimanale", style="AppTitle.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(
            header,
            text="Naviga tra i giorni, aggiungi impegni e mantieni tutto in ordine.",
            style="SurfaceSubtle.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(6, 0))

        nav = ttk.Frame(self, padding=(0, 12)) #navigazione giorni
        nav.grid(row=1, column=0, sticky="ew")
        nav.columnconfigure(1, weight=1)

        self.btn_prev = ttk.Button(nav, text="◀", width=3, command=self._show_previous_day) # Pulsante giorno precedente
        self.btn_prev.grid(row=0, column=0, sticky="w")

        self.lbl_day = ttk.Label(nav, text="", font=("Helvetica", 12, "bold")) # Etichetta con il giorno mostrato attualmente
        self.lbl_day.grid(row=0, column=1, sticky="n")

        self.btn_next = ttk.Button(nav, text="▶", width=3, command=self._show_next_day) # Pulsante giorno successivo
        self.btn_next.grid(row=0, column=2, sticky="e")

        form = ttk.LabelFrame(self, text="Aggiungi attività", style="Surface.TLabelframe")
        form.grid(row=2, column=0, sticky="ew", pady=(0, 16))
        for col in range(4): # Rendo elastiche solo le colonne con input lunghi (1 e 3)
            form.columnconfigure(col, weight=1 if col in (1, 3) else 0)

        ttk.Label(form, text="Giorno:", style="SurfaceSubtle.TLabel").grid(row=0, column=0, sticky="w", padx=(6, 0), pady=6) # Campo: Giorno
        self.combo_day = ttk.Combobox(form, values=self.DAYS, state="readonly", width=12, style="Planner.TCombobox")
        self.combo_day.current(self.current_day_index)
        self.combo_day.grid(row=0, column=1, sticky="w", pady=6)

        ttk.Label(form, text="Orario (HH:MM):", style="SurfaceSubtle.TLabel").grid(row=0, column=2, sticky="w", padx=(12, 0), pady=6) # Campo: Orario
        self.entry_time = ttk.Entry(form, width=10)
        self.entry_time.grid(row=0, column=3, sticky="w", pady=6)

        ttk.Label(form, text="Attività:", style="SurfaceSubtle.TLabel").grid(row=1, column=0, sticky="w", padx=(6, 0), pady=6) # Campo: Attività
        self.entry_subject = ttk.Entry(form)
        self.entry_subject.grid(row=1, column=1, sticky="ew", pady=6)

        ttk.Label(form, text="Note:", style="SurfaceSubtle.TLabel").grid(row=1, column=2, sticky="w", padx=(12, 0), pady=6) # Campo: Note (opzionali)
        self.entry_notes = ttk.Entry(form)
        self.entry_notes.grid(row=1, column=3, sticky="ew", pady=6)

        self.btn_add = ttk.Button(form, text="Aggiungi", command=self._add_activity, style="Primary.TButton") # Pulsante di aggiunta
        self.btn_add.grid(row=2, column=0, columnspan=4, sticky="e", padx=6, pady=(8, 6))

        table_frame = ttk.LabelFrame(self, text="Attività del giorno", style="Surface.TLabelframe") # TABELLA (Treeview)
        table_frame.grid(row=3, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        columns = ("time", "subject", "notes") # Definisci le colonne logiche della Treeview
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=8)
        headings = { # Intestazioni con possibilità di ordinamento cliccando sul titolo
            "time": "Orario",
            "subject": "Attività",
            "notes": "Note",
        }
        for col in columns: 
            self.tree.heading(col, text=headings[col], command=lambda c=col: self._sort_by(c))
            anchor = "center" if col == "time" else "w"
            width = 110 if col == "time" else 220
            self.tree.column(col, anchor=anchor, width=width)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview) # Scrollbar verticale collegata alla treeview
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew") 
        scrollbar.grid(row=0, column=1, sticky="ns")

        actions = ttk.Frame(table_frame, style="Surface.TFrame") # Barra azioni sotto la tabella (qui solo rimozione selezione)
        actions.grid(row=1, column=0, columnspan=2, sticky="e", pady=(8, 0))
        ttk.Button(actions, text="Rimuovi selezionato", command=self._remove_selected_activity).pack(anchor="e")

        self.lbl_hint = ttk.Label(self, text="", anchor="w", style="Subtle.TLabel") # Etichetta (es. numero attività del giorno)
        self.lbl_hint.grid(row=4, column=0, sticky="w", pady=(12, 0))

    #navigazione giorni
    def _show_previous_day(self):
        if self.current_day_index > 0:
            self.current_day_index -= 1
            self._refresh_day()

    def _show_next_day(self):
        if self.current_day_index < len(self.DAYS) - 1:
            self.current_day_index += 1
            self._refresh_day()

    def _refresh_day(self): #aggiornamento vista
        day = self.DAYS[self.current_day_index]
        self.lbl_day.config(text=day)
        self.combo_day.current(self.current_day_index)

        # Disabilita i bottoni ai bordi per non andare fuori range
        if self.current_day_index == 0:
            self.btn_prev.state(["disabled"])
        else:
            self.btn_prev.state(["!disabled"])

        if self.current_day_index == len(self.DAYS) - 1:
            self.btn_next.state(["disabled"])
        else:
            self.btn_next.state(["!disabled"])

        # Svuoto e ricarico la tabella così sono certo di mostrare lo stato aggiornato del JSON
        for row in self.tree.get_children():
            self.tree.delete(row)

        entries = sorted(self.schedule[day], key=lambda item: item["time"]) # Ordina per orario
        for index, entry in enumerate(entries):
            tag = "evenrow" if index % 2 == 0 else "oddrow"
            self.tree.insert("", "end", values=(entry["time"], entry["subject"], entry["notes"]), tags=(tag,))

        if entries:
            self.lbl_hint.config(text=f"{len(entries)} attività pianificate per {day}.")
        else:
            self.lbl_hint.config(text=f"Nessuna attività programmata per {day}.")
        self._apply_tree_styles()

    def _apply_tree_styles(self): #applica caratteristiche tema 
        if not hasattr(self, "tree"):
            return
        palette = getattr(self.winfo_toplevel(), "_planner_palette", None)
        if palette is not None:
            even_bg = palette.surface
            odd_bg = palette.alternate
            fg = palette.text
        else:
            even_bg = "#FFFFFF"
            odd_bg = "#F1F5F9"
            fg = "#111111"
        self.tree.tag_configure("evenrow", background=even_bg, foreground=fg)
        self.tree.tag_configure("oddrow", background=odd_bg, foreground=fg)

    def _on_theme_change(self, _event=None): # Richiamato quando cambia il tema: riapplica le palette
        self._apply_tree_styles()

    def _add_activity(self): #aggiunta e validazione
        selected_day = self.combo_day.get()
        time_value = self.entry_time.get().strip()
        subject_value = self.entry_subject.get().strip()
        notes_value = self.entry_notes.get().strip()

        if not time_value or not subject_value: # Campi minimi richiesti: orario + attività
            messagebox.showwarning("Campi obbligatori", "Inserisci almeno orario e attività.")
            return

        try:
            datetime.strptime(time_value, "%H:%M") # Validazione formato orario: deve essere HH:MM 24h
        except ValueError:
            messagebox.showwarning("Formato orario non valido", "Usa il formato 24h HH:MM.")
            return

        entry = { ## Crea il record e aggiungilo alla lista del giorno selezionato
            "time": time_value,
            "subject": subject_value,
            "notes": notes_value,
        }
        self.schedule[selected_day].append(entry)
        self._persist_schedule() # salva subito su disco

        if selected_day == self.DAYS[self.current_day_index]: 
            self._refresh_day() # Se stai visualizzando proprio quel giorno, aggiorna la tabella

        self.entry_time.delete(0, tk.END) # Svuota i campi e rimetti il focus sull'orario
        self.entry_subject.delete(0, tk.END)
        self.entry_notes.delete(0, tk.END)
        self.entry_time.focus_set()

    def _persist_schedule(self):
        # Salvo immediatamente così se l'app si chiude non ce problema
        save_schedule(self.schedule)

    def _sort_by(self, column: str):
        day = self.DAYS[self.current_day_index]
        entries = self.schedule[day]
        if not entries:
            return

        if not hasattr(self, "_sort_state"):
            self._sort_state = {}

        current_desc = self._sort_state.get(column, False)
        reverse = not current_desc

        # Selettore chiave di ordinamento per ogni colonna
        if column == "time":
            key_fn = lambda item: item["time"]
        elif column == "subject":
            key_fn = lambda item: item["subject"].lower()
        else:
            key_fn = lambda item: item["notes"].lower()

        # Riordino la lista in place (senza creare un altra lista) così la successiva chiamata a _refresh_day mantiene l'ordinamento scelto
        entries.sort(key=key_fn, reverse=reverse)
        self._sort_state[column] = reverse
        self._refresh_day()

    def _remove_selected_activity(self): 
        selection = self.tree.selection() # tuple di ID selezionati (qui usiamo la prima riga)
        if not selection:
            messagebox.showinfo("Seleziona un'attività", "Seleziona un'attività da rimuovere.")
            return

        item_id = selection[0]
        values = self.tree.item(item_id, "values") # tuple: (time, subject, notes)
        if not values or len(values) < 3:
            messagebox.showwarning("Elemento non valido", "Impossibile identificare l'attività selezionata.")
            return

        time_value, subject_value, notes_value = values 
        if not messagebox.askyesno("Conferma rimozione", f"Vuoi eliminare l'attività '{subject_value}' delle {time_value}?"): # Conferma utente prima dell'eliminazione
            return

        day = self.DAYS[self.current_day_index] # Cerca la prima occorrenza che combaci esattamente e rimuovila
        entries = self.schedule[day]
        for idx, entry in enumerate(entries):
            if (
                entry.get("time") == time_value 
                and entry.get("subject") == subject_value
                and entry.get("notes") == notes_value
            ):
                # Rimuovo e salvo subito
                entries.pop(idx) # rimuovi dalla lista in memoria
                self._persist_schedule() # salva su disco subito
                self._refresh_day() # aggiorna UI
                return

        # Se arrivo qui significa che l'utente ha probabilmente aggiornato la giornata mentre la dialog era aperta
        messagebox.showwarning("Elemento non trovato", "L'attività selezionata non è più disponibile.")


def create_schedule_tab(parent: tk.Widget) -> ttk.Frame: # Factory function per integrare la tab nel Notebook principale
    return ScheduleTab(parent)
