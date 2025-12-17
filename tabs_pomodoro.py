import tkinter as tk
from datetime import date
from tkinter import messagebox, ttk

from report import fmt_mm, somma
from storage import FILE_NAME, load_data, save_data


def fmt_mmss(sec: int) -> str: #Formatta i secondi come MM:SS, senza numeri negativi
    sec = max(0, int(sec))
    minutes, seconds = divmod(sec, 60)
    return f"{minutes:02d}:{seconds:02d}"

class Pomodoro(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=12, style="Background.TFrame")

        self.tempo_studiato = load_data(FILE_NAME) # inizializza il Frame con padding e stile

        self.state = "idle" # stato corrente del timer: nessuna fase attiva
        self.after_id = None # id della callback schedulata con after(); serve per poterla annullare
        self.sec_target = 0 # durata della fase corrente in secondi (obiettivo)
        self.sec_restanti = 0 # secondi rimanenti nella fase corrente
        self.minimo_salvataggio_min = 1 # soglia minima di minuti per salvare una sessione
        self.materia_corrente = "" # nome materia normalizzato (minuscolo) della sessione in corso

        self.var_materia = tk.StringVar() # testo dell'Entry "Materia"
        self.var_studio = tk.IntVar(value=25) # minuti fase di studio (Spinbox)
        self.var_riposo = tk.IntVar(value=5) # minuti fase di riposo (Spinbox)
        self.var_auto = tk.BooleanVar(value=False) # se True, dopo il riposo riparte in automatico lo studio

        self.var_timer = tk.StringVar(value="00:00") # testo mostrato al centro del timer (MM:SS)
        self.var_fase = tk.StringVar(value="_") # descrizione della fase (es. "Studio di Matematica")
        self.var_info = tk.StringVar(value="Pronto!") # barra info in basso usata come mini-log
        self.tree_materie = None  # riferimento alla Treeview del riepilogo materie

        self._build_ui() # crea tutti i widget (canvas del timer, pulsanti, tabella, ecc.)
        self._update_stats() # calcola e mostra i totali (oggi/settimana/mese) e popola la tabella

    
    def _build_ui(self):
        # Layout base: 2 colonne (sinistra contenuti, destra card del timer)
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(1, weight=1)

        left_col = ttk.Frame(self, style="Background.TFrame") # Colonna sinistra
        left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
        left_col.columnconfigure(0, weight=1)

        frame_top = ttk.Frame(left_col, style="Surface.TFrame", padding=16) # Card impostazioni in alto a sinistra
        frame_top.grid(row=0, column=0, sticky="nsew")
        frame_top.columnconfigure(1, weight=1)

        ttk.Label(frame_top, text="Materia:", style="Surface.TLabel").grid(row=0, column=0, sticky="w") # Campo materia
        ttk.Entry(frame_top, textvariable=self.var_materia, width=28).grid(row=0, column=1, columnspan=3, sticky="we")

        ttk.Label(frame_top, text="Studio (min):", style="Surface.TLabel").grid(row=1, column=0, sticky="w", pady=(8, 0)) # Spinbox durate studio/pausa
        ttk.Spinbox(frame_top, from_=1, to=240, textvariable=self.var_studio, width=6).grid(row=1, column=1, sticky="w", pady=(8, 0))

        ttk.Label(frame_top, text="Pausa (min):", style="Surface.TLabel").grid(row=1, column=2, sticky="w", pady=(8, 0))  
        ttk.Spinbox(frame_top, from_=1, to=120, textvariable=self.var_riposo, width=6).grid(row=1, column=3, sticky="w", pady=(8, 0))

        ttk.Checkbutton(  # Switch auto-continua    
            frame_top,
            text="Auto-continua i cicli",
            variable=self.var_auto,
            style="Surface.TCheckbutton",
        ).grid(row=2, column=0, columnspan=4, sticky="w", pady=(12, 0))

        frame_stats = ttk.LabelFrame(left_col, text="Statistiche", style="Surface.TLabelframe") # Card statistiche
        frame_stats.grid(row=1, column=0, sticky="nsew", pady=(16, 0))
        self.var_stat_oggi = tk.StringVar()
        self.var_stat_sett = tk.StringVar()
        self.var_stat_mese = tk.StringVar()
        ttk.Label(frame_stats, text="Oggi:", style="SurfaceSubtle.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(frame_stats, textvariable=self.var_stat_oggi, style="Surface.TLabel").grid(row=0, column=1, sticky="w")
        ttk.Label(frame_stats, text="Settimana:", style="SurfaceSubtle.TLabel").grid(row=1, column=0, sticky="w", pady=(4, 0))
        ttk.Label(frame_stats, textvariable=self.var_stat_sett, style="Surface.TLabel").grid(row=1, column=1, sticky="w", pady=(4, 0))
        ttk.Label(frame_stats, text="Mese:", style="SurfaceSubtle.TLabel").grid(row=2, column=0, sticky="w", pady=(4, 0))
        ttk.Label(frame_stats, textvariable=self.var_stat_mese, style="Surface.TLabel").grid(row=2, column=1, sticky="w", pady=(4, 0))

        timer_card = ttk.Frame(self, style="Surface.TFrame", padding=24) # Colonna destra: card del timer circolare
        timer_card.grid(row=0, column=1, sticky="n")
        timer_card.columnconfigure(0, weight=1)

        timer_frame = ttk.Frame(timer_card, style="Surface.TFrame") # Contenitore elementi del timer
        timer_frame.grid(row=0, column=0)

        base_bg = self._get_base_background() # Canvas per cerchio di progresso
        self.canvas_timer = tk.Canvas(timer_frame, width=220, height=220, highlightthickness=0, bg=base_bg)
        self.canvas_timer.grid(row=0, column=0, padx=4)

        self.arc_background = self.canvas_timer.create_oval(10, 10, 210, 210, outline="#d1d5db", width=14) # Cerchio di sfondo e arco di progresso
        self.arc_progress = self.canvas_timer.create_arc(10, 10, 210, 210, start=90, extent=0, style="arc", outline="#4f46e5", width=14)

        self.lbl_timer = ttk.Label(timer_frame, textvariable=self.var_timer, font=("Helvetica", 32, "bold"), style="Surface.TLabel") # Etichetta grande con il tempo MM:SS dentro al cerchio
        self.lbl_timer.place(in_=self.canvas_timer, relx=0.5, rely=0.45, anchor="center")

        ttk.Label(timer_card, textvariable=self.var_fase, style="SurfaceSubtle.TLabel").grid(row=1, column=0, pady=(12, 0)) # Sottotitolo con la fase corrente (es. "Studio di ...")

        # Pulsanti Start/Pausa/Stop
        frame_btn = ttk.Frame(timer_card, style="Surface.TFrame")
        frame_btn.grid(row=2, column=0, pady=(18, 0))
        self.btn_start = ttk.Button(frame_btn, text="Start", command=self.on_start, style="Primary.TButton")
        self.btn_start.grid(row=0, column=0, padx=5)
        self.btn_pause = ttk.Button(frame_btn, text="Pausa", command=self.on_pause, state="disabled")
        self.btn_pause.grid(row=0, column=1, padx=5)
        self.btn_stop = ttk.Button(frame_btn, text="Stop", command=self.on_stop, state="disabled")
        self.btn_stop.grid(row=0, column=2, padx=5)

        # Tabella riepilogo per materia (oggi/settimana/mese/totale)
        frame_subjects = ttk.LabelFrame(self, text="Dettaglio materie", style="Surface.TLabelframe")
        frame_subjects.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(16, 0))

        container = ttk.Frame(frame_subjects, style="Surface.TFrame")
        container.pack(fill="both", expand=True)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=1)

        columns = ("materia", "oggi", "settimana", "mese", "totale")
        self.tree_materie = ttk.Treeview(container, columns=columns, show="headings", height=10)
        for col, title in ( # Clic sulle intestazioni = ordina per colonna
            ("materia", "Materia"),
            ("oggi", "Oggi"),
            ("settimana", "Settimana"),
            ("mese", "Mese"),
            ("totale", "Totale"),
        ):
            self.tree_materie.heading(col, text=title, command=lambda c=col: self._sort_tree_by(c))
        self.tree_materie.column("materia", anchor="w", width=160)
        self.tree_materie.column("oggi", anchor="center", width=90)
        self.tree_materie.column("settimana", anchor="center", width=110)
        self.tree_materie.column("mese", anchor="center", width=90)
        self.tree_materie.column("totale", anchor="center", width=90)

        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.tree_materie.yview)
        self.tree_materie.configure(yscrollcommand=scrollbar.set)

        self.tree_materie.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")


        info_bar = ttk.Frame(self, style="Surface.TFrame", padding=(16, 10)) # Barra info/log in basso  
        info_bar.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(16, 0))
        ttk.Label(info_bar, textvariable=self.var_info, anchor="w", style="Surface.TLabel").pack(fill="x")

        self._update_progress_colors()
        self._apply_tree_styles()
        root = self.winfo_toplevel() # Ascolta cambi tema
        try:
            root.bind("<<PlannerThemeChanged>>", self._handle_theme_change, add="+")
        except Exception:
            pass

    #Bottoni
    def on_start(self):
        materia = self.var_materia.get().strip().lower()
        if not materia:
            messagebox.showwarning("Attenzione!", "Inserisci una materia.")
            return

        try:
            minuti_studio = int(self.var_studio.get())
            minuti_riposo = int(self.var_riposo.get())
        except (tk.TclError, ValueError):
            messagebox.showwarning("Attenzione!", "Inserisci valori numerici validi per i minuti.")
            return

        # Normalizzo subito il nome materia così le statistiche non si duplicano per causa maiuscole/maiuscole
        if minuti_studio <= 0 or minuti_riposo <= 0:
            messagebox.showwarning("Attenzione!", "Minuti di studio o pausa devono essere superiori a 0.")
            return

        # Passa a fase "studio"
        self.var_materia.set(materia) 
        self.materia_corrente = materia
        self._switch_to("studio", seconds=minuti_studio * 60)
        self.var_info.set("Sessione avviata")
        self._tick()
    
    def on_pause(self):
        if self.state == "studio":
            self._cancel_after()
            self.state = "pausa_studio"
            self.var_fase.set(f"Pausa studio di {self.materia_corrente.capitalize()}")
            self.btn_pause.config(text="Riprendi")
            self._log("Studio in pausa")
        elif self.state == "riposo":
            self._cancel_after()
            self.state = "pausa_riposo"
            self.var_fase.set("Pausa riposo")
            self.btn_pause.config(text="Riprendi")
            self._log("Riposo in pausa")
        elif self.state in ("pausa_studio", "pausa_riposo"):
            # Quando l'utente riprende, ripristiniamo i timer senza perdere i secondi residui
            self.btn_pause.config(text="Pausa")
            if self.state == "pausa_studio":
                self._switch_to("studio", seconds=self.sec_restanti, lock_inputs=True, change_buttons=False, reset_target=False)
                self._log("Studio ripreso")
            else:
                self._switch_to("riposo", seconds=self.sec_restanti, lock_inputs=True, change_buttons=False, reset_target=False)
                self._log("Riposo ripreso")
            self._tick()
            
    def on_stop(self) :
        self._cancel_after()
        if self.state in ("studio", "pausa_studio"):
            sec_fatti = self.sec_target - self.sec_restanti
            minuti_fatti = sec_fatti // 60
            if minuti_fatti >= self.minimo_salvataggio_min: #se il tempo studiato e piu del minimo salva
                self._salva(self.materia_corrente, minuti_fatti)
                self._log(f"Sessione interrotta e salvata ({minuti_fatti} min).")
                self._update_stats()
            else:
                self._log("Interrotto: meno di 1 minuto, non salvo.") #altrimenti non lo fa
        else:
            self._log("Timer fermato.")
        self._reset_to_idle()

    def _switch_to(self, new_state: str, seconds: int, lock_inputs: bool = True, change_buttons: bool = True, reset_target: bool = True):
        # Questa funzione centralizza tutti i piccoli dettagli quando passiamo da lavoro a pausa (e viceversa)
        self._cancel_after()
        self.state = new_state
        if reset_target:
            self.sec_target = int(seconds)
        self.sec_restanti = int(seconds)
        self.var_timer.set(fmt_mmss(self.sec_restanti))
        self._update_progress_arc()
        if new_state == "studio":
            self.var_fase.set(f"Studio di {self.materia_corrente.capitalize()}")
            self.btn_pause.config(text="Pausa")
            if change_buttons:
                self._set_buttons(running=True)
            if lock_inputs:
                self._lock_inputs(True)
        elif new_state == "riposo":
            self.var_fase.set("Riposo")
            self.btn_pause.config(text="Pausa")
            if change_buttons:
                self._set_buttons(running=True)
            if lock_inputs:
                self._lock_inputs(True)

    def _reset_to_idle(self):
        self._cancel_after()
        self.state = "idle"
        self.sec_target = 0
        self.sec_restanti = 0
        self.var_timer.set("00:00")
        self.var_fase.set("—")
        self._set_buttons(running=False)
        self._lock_inputs(False)
        self._reset_progress_arc()

    def _reset_after_cycle(self, message: str = "Pronto!"):
        self._reset_to_idle()
        self._log(message)

    def _tick(self):
        self.after_id = None
        self.var_timer.set(fmt_mmss(self.sec_restanti)) # aggiorna il testo MM:SS sullo schermo
        self._update_progress_arc() # aggiorna il cerchio di avanzamento

        # Richiamo _tick ogni secondo fino a completare la fase
        if self.sec_restanti <= 0: ##Se ho finito i secondi, gestisco il cambio fase
            self._handle_phase_complete()
            return
        self.sec_restanti -= 1 # Altrimenti decremento e pianifico il prossimo tick
        self.after_id = self.after(1000, self._tick)

    def _handle_phase_complete(self): #Cosa succede quando termina una fase (studio o riposo)
        current_state = self.state
        if current_state == "studio": # Salva la sessione completata se ha almeno il minimo
            minuti_fatti = (self.sec_target // 60) if self.sec_target else 0
            if minuti_fatti >= self.minimo_salvataggio_min:
                self._salva(self.materia_corrente, minuti_fatti)
                self._update_stats()
                self._log(f"Sessione completata ({minuti_fatti} min).")
            else:
                # Evito di riempire il database con sessioni da pochi secondi
                self._log("Sessione troppo breve, non salvo.")

            minuti_riposo = int(self.var_riposo.get()) # Passo al riposo, o chiudo il ciclo se pausa=0
            if minuti_riposo > 0:
                self._switch_to("riposo", seconds=minuti_riposo * 60)
                self._tick()
            else:
                self._reset_after_cycle("Sessione completata.")

        elif current_state == "riposo":
            self._log("Pausa terminata.")
            if self.var_auto.get():  # Se auto-continua, riparte un nuovo studio
                minuti_studio = int(self.var_studio.get())
                if minuti_studio > 0:
                    self._switch_to("studio", seconds=minuti_studio * 60)
                    self._tick()
                else:
                    self._reset_after_cycle()
            else:
                self._reset_after_cycle("Pausa terminata. Premi Start per continuare.")

        else:
            self._reset_after_cycle()

    def _set_buttons(self, running: bool):
        # Abilita/disabilita i bottoni in base allo stato del timer
        if running:
            self.btn_start.config(state="disabled")
            self.btn_pause.config(state="normal", text="Pausa")
            self.btn_stop.config(state="normal")
        else:
            self.btn_start.config(state="normal")
            self.btn_pause.config(state="disabled", text="Pausa")
            self.btn_stop.config(state="disabled")

    def _lock_inputs(self, locked: bool):
        # Blocca/sblocca solo i controlli di input (Entry/Spinbox/Checkbutton)
        state = "disabled" if locked else "normal"
        def _walk(widget):
            if isinstance(widget, (ttk.Entry, ttk.Spinbox, ttk.Checkbutton)):
                try:
                    widget.configure(state=state)
                except tk.TclError:
                    pass
            for child in widget.winfo_children():
                _walk(child)

        _walk(self)

    def _cancel_after(self):
        if self.after_id is not None:
            try:
                self.after_cancel(self.after_id)
            except Exception:
                pass
            self.after_id = None

    def _log(self, msg: str):
        # La barra inferiore funge da mini log in tempo reale
        self.var_info.set(msg)

    def _salva(self, materia: str, minuti: int):
        # Accoda una sessione alla materia e salva su file JSON
        if minuti <= 0:
            return
        oggi = date.today().isoformat()
        self.tempo_studiato.setdefault(materia, [])
        self.tempo_studiato[materia].append({"data": oggi, "minuti": int(minuti)})
        save_data(self.tempo_studiato, FILE_NAME)

    def _reset_progress_arc(self):
        #Azzera l’arco di progresso nel canvas
        if hasattr(self, "canvas_timer"):
            self.canvas_timer.itemconfigure(self.arc_progress, extent=0)
            self._update_progress_colors()

    def _update_progress_arc(self):
        if not hasattr(self, "canvas_timer"):
            return
        if self.sec_target <= 0:
            extent = 0
        else:
            progress = (self.sec_target - self.sec_restanti) / self.sec_target
            extent = max(0, min(360, progress * 360))
        self.canvas_timer.itemconfigure(self.arc_progress, extent=-extent)

    def _update_progress_colors(self):
        # Aggiorna i colori del canvas in base alla palette del tema
        if not hasattr(self, "canvas_timer"):
            return
        palette = getattr(self.winfo_toplevel(), "_planner_palette", None)
        if palette is not None:
            background = palette.background
            arc_bg = palette.border
            arc_fg = palette.accent
        else:
            background = self._get_base_background()
            arc_bg = "#d1d5db"
            arc_fg = "#4f46e5"
        self.canvas_timer.configure(bg=background)
        self.canvas_timer.itemconfigure(self.arc_background, outline=arc_bg)
        self.canvas_timer.itemconfigure(self.arc_progress, outline=arc_fg)

    def _handle_theme_change(self, _event=None):
        self._update_progress_colors()
        self._update_progress_arc()
        self._apply_tree_styles()

    def _get_base_background(self) -> str:
        try:
            return self.winfo_toplevel().cget("background")
        except Exception:
            return "#ffffff"

    def _update_stats(self):
        # Aggiorna i riassunti Oggi/Settimana/Mese e la tabella per materia
        try:
            ogg  = somma(self.tempo_studiato, "oggi")
            sett = somma(self.tempo_studiato, "settimana")
            mese = somma(self.tempo_studiato, "mese")
            self.var_stat_oggi.set(fmt_mm(ogg))
            self.var_stat_sett.set(fmt_mm(sett))
            self.var_stat_mese.set(fmt_mm(mese))
            self._update_subject_breakdown()
        except Exception: # In caso di dati corrotti/errore, mostra trattini e svuota tabella
            self.var_stat_oggi.set("—")
            self.var_stat_sett.set("—")
            self.var_stat_mese.set("—")
            self._clear_subject_breakdown()

    def _apply_tree_styles(self):
        if self.tree_materie is None:
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
        # Alterno i colori per facilitare la lettura delle righe (striped table effect)
        self.tree_materie.tag_configure("evenrow", background=even_bg, foreground=fg)
        self.tree_materie.tag_configure("oddrow", background=odd_bg, foreground=fg)

    def _update_subject_breakdown(self):
        #Ricostruisce la tabella per materia con le somme per periodo
        if self.tree_materie is None:
            return
        self.tree_materie.delete(*self.tree_materie.get_children()) # Pulisce e reinserisce tutto
        if not self.tempo_studiato:
            return

        # Preparo una vista tabellare con oggi/settimana/mese così posso confrontare le materie a colpo d'occhio
        rows = []
        for materia, sessions in self.tempo_studiato.items():
            dataset = {materia: sessions}
            try:
                oggi = somma(dataset, "oggi")
                settimana = somma(dataset, "settimana")
                mese = somma(dataset, "mese")
            except Exception:
                oggi = settimana = mese = 0
            totale = sum(int(s.get("minuti", 0)) for s in sessions)
            rows.append(
                {
                    "materia": materia,
                    "oggi": oggi,
                    "settimana": settimana,
                    "mese": mese,
                    "totale": totale,
                }
            )

        self._insert_tree_rows(rows)

    def _clear_subject_breakdown(self):
        if self.tree_materie is not None:
            self.tree_materie.delete(*self.tree_materie.get_children())

    def _insert_tree_rows(self, rows):
        # Inserisce righe nella Treeview con tag per riga pari/dispari e tag raw_<materia>
        if self.tree_materie is None:
            return
        for index, row in enumerate(rows):
            tags = (
                f"raw_{row['materia']}",  # serve per risalire alla chiave
                "evenrow" if index % 2 == 0 else "oddrow", # zebra striping
            )
            self.tree_materie.insert(
                "",
                "end",
                values=(
                    row["materia"].capitalize(),
                    fmt_mm(row["oggi"]),
                    fmt_mm(row["settimana"]),
                    fmt_mm(row["mese"]),
                    fmt_mm(row["totale"]),
                ),
                tags=tags,
            )
        self._apply_tree_styles()

    def _sort_tree_by(self, column):
        if self.tree_materie is None:
            return
        
        # Ordina la tabella per colonna (materia/oggi/settimana/mese/totale)
        current_rows = []
        for materia, sessions in self.tempo_studiato.items():
            dataset = {materia: sessions}
            try:
                oggi = somma(dataset, "oggi")
                settimana = somma(dataset, "settimana")
                mese = somma(dataset, "mese")
            except Exception:
                oggi = settimana = mese = 0
            totale = sum(int(s.get("minuti", 0)) for s in sessions)
            row = {
                "materia": materia,
                "oggi": oggi,
                "settimana": settimana,
                "mese": mese,
                "totale": totale,
            }
            current_rows.append(row)

        if not current_rows:
            return

        descending = getattr(self, "_sort_desc", {})
        descending[column] = not descending.get(column, False)
        self._sort_desc = descending

        # Chiave di ordinamento: alfabetica per materia, numerica per le altre
        if column == "materia":
            key_fn = lambda r: r["materia"].lower()
        else:
            key_fn = lambda r: r[column]

        ordered = sorted(current_rows, key=key_fn, reverse=descending[column])
        self.tree_materie.delete(*self.tree_materie.get_children())
        self._insert_tree_rows(ordered)


def create_pomodoro_frame(parent):
    # Factory function per integrare la tab nel Notebook principale
    return Pomodoro(parent)
