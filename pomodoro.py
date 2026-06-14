import tkinter as tk
from datetime import date
from tkinter import messagebox, ttk

from report import fmt_mm, somma
from storage import FILE_NAME, load_data, save_data


def fmt_mmss(sec: int) -> str:
    sec = max(0, int(sec))
    minutes, seconds = divmod(sec, 60)
    return f"{minutes:02d}:{seconds:02d}"


class Pomodoro(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=18, style="Background.TFrame")

        self.tempo_studiato = load_data(FILE_NAME)

        self.state = "idle"
        self.after_id = None
        self.sec_target = 0
        self.sec_restanti = 0
        self.minimo_salvataggio_min = 1
        self.materia_corrente = ""

        self.var_materia = tk.StringVar()
        self.var_studio = tk.IntVar(value=25)
        self.var_riposo = tk.IntVar(value=5)
        self.var_auto = tk.BooleanVar(value=False)

        self.var_timer = tk.StringVar(value="25:00")
        self.var_fase = tk.StringVar(value="Studio")
        self.var_info = tk.StringVar(value="Pronto!")

        self.var_stat_oggi = tk.StringVar(value="—")
        self.var_stat_sett = tk.StringVar(value="—")
        self.var_stat_mese = tk.StringVar(value="—")

        self.tree_materie = None

        self._build_ui()
        self._update_stats()

    def _build_ui(self):
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(1, weight=1)

        # Colonna sinistra
        left_col = ttk.Frame(self, style="Background.TFrame")
        left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 18))
        left_col.columnconfigure(0, weight=1)

        # Card impostazioni
        settings_card = ttk.LabelFrame(
            left_col,
            text="Impostazioni",
            style="Surface.TLabelframe",
        )
        settings_card.grid(row=0, column=0, sticky="ew")
        settings_card.columnconfigure(1, weight=1)
        settings_card.columnconfigure(3, weight=1)

        ttk.Label(
            settings_card,
            text="Materia",
            style="SurfaceSubtle.TLabel",
        ).grid(row=0, column=0, sticky="w", padx=(4, 10), pady=(4, 8))

        self.entry_materia = ttk.Entry(
            settings_card,
            textvariable=self.var_materia,
        )
        self.entry_materia.grid(row=0, column=1, columnspan=3, sticky="ew", pady=(4, 8))

        ttk.Label(
            settings_card,
            text="Studio (min)",
            style="SurfaceSubtle.TLabel",
        ).grid(row=1, column=0, sticky="w", padx=(4, 10), pady=8)

        self.spin_studio = ttk.Spinbox(
            settings_card,
            from_=1,
            to=240,
            textvariable=self.var_studio,
            width=8,
        )
        self.spin_studio.grid(row=1, column=1, sticky="w", pady=8)

        ttk.Label(
            settings_card,
            text="Pausa (min)",
            style="SurfaceSubtle.TLabel",
        ).grid(row=1, column=2, sticky="w", padx=(18, 10), pady=8)

        self.spin_riposo = ttk.Spinbox(
            settings_card,
            from_=1,
            to=120,
            textvariable=self.var_riposo,
            width=8,
        )
        self.spin_riposo.grid(row=1, column=3, sticky="w", pady=8)

        self.check_auto = ttk.Checkbutton(
            settings_card,
            text="Auto-continua i cicli",
            variable=self.var_auto,
            style="Surface.TCheckbutton",
        )
        self.check_auto.grid(row=2, column=0, columnspan=4, sticky="w", padx=(0, 0), pady=(12, 2))

        # Card statistiche
        stats_card = ttk.LabelFrame(
            left_col,
            text="Statistiche",
            style="Surface.TLabelframe",
        )
        stats_card.grid(row=1, column=0, sticky="ew", pady=(18, 0))
        stats_card.columnconfigure(0, weight=1)
        stats_card.columnconfigure(1, weight=1)
        stats_card.columnconfigure(2, weight=1)

        self._build_stat_box(
            stats_card,
            column=0,
            label="Oggi",
            variable=self.var_stat_oggi,
        )

        self._build_stat_box(
            stats_card,
            column=1,
            label="Settimana",
            variable=self.var_stat_sett,
        )

        self._build_stat_box(
            stats_card,
            column=2,
            label="Mese",
            variable=self.var_stat_mese,
        )

        # Card timer
        timer_card = ttk.LabelFrame(
            self,
            text="Timer",
            style="Surface.TLabelframe",
        )
        timer_card.grid(row=0, column=1, sticky="nsew")
        timer_card.columnconfigure(0, weight=1)

        ttk.Label(
            timer_card,
            textvariable=self.var_info,
            style="SurfaceSubtle.TLabel",
            anchor="center",
        ).grid(row=0, column=0, sticky="ew", pady=(2, 12))

        timer_area = ttk.Frame(timer_card, style="Surface.TFrame")
        timer_area.grid(row=1, column=0, sticky="n")
        timer_area.columnconfigure(0, weight=1)

        base_bg = self._get_timer_background()
        self.canvas_timer = tk.Canvas(
            timer_area,
            width=250,
            height=250,
            highlightthickness=0,
            bg=base_bg,
        )
        self.canvas_timer.grid(row=0, column=0, padx=4, pady=(0, 4))

        self.arc_background = self.canvas_timer.create_oval(
            18,
            18,
            232,
            232,
            outline="#E4E7F5",
            width=16,
        )

        self.arc_progress = self.canvas_timer.create_arc(
            18,
            18,
            232,
            232,
            start=90,
            extent=0,
            style="arc",
            outline="#5465FF",
            width=16,
        )

        self.lbl_timer = ttk.Label(
            timer_area,
            textvariable=self.var_timer,
            font=("Inter", 36, "bold"),
            style="Surface.TLabel",
        )
        self.lbl_timer.place(
            in_=self.canvas_timer,
            relx=0.5,
            rely=0.45,
            anchor="center",
        )

        self.lbl_phase = ttk.Label(
            timer_area,
            textvariable=self.var_fase,
            style="SurfaceSubtle.TLabel",
        )
        self.lbl_phase.place(
            in_=self.canvas_timer,
            relx=0.5,
            rely=0.60,
            anchor="center",
        )

        buttons_frame = ttk.Frame(timer_card, style="Surface.TFrame")
        buttons_frame.grid(row=2, column=0, sticky="ew", pady=(18, 2))
        buttons_frame.columnconfigure(0, weight=1)
        buttons_frame.columnconfigure(1, weight=1)
        buttons_frame.columnconfigure(2, weight=1)

        self.btn_start = ttk.Button(
            buttons_frame,
            text="Avvia",
            command=self.on_start,
            style="Primary.TButton",
        )
        self.btn_start.grid(row=0, column=0, sticky="ew", padx=(0, 6))

        self.btn_pause = ttk.Button(
            buttons_frame,
            text="Pausa",
            command=self.on_pause,
            state="disabled",
        )
        self.btn_pause.grid(row=0, column=1, sticky="ew", padx=6)

        self.btn_stop = ttk.Button(
            buttons_frame,
            text="Stop",
            command=self.on_stop,
            state="disabled",
        )
        self.btn_stop.grid(row=0, column=2, sticky="ew", padx=(6, 0))

        # Tabella dettaglio materie
        subjects_card = ttk.LabelFrame(
            self,
            text="Dettaglio materie",
            style="Surface.TLabelframe",
        )
        subjects_card.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(18, 0))
        subjects_card.columnconfigure(0, weight=1)
        subjects_card.rowconfigure(0, weight=1)

        columns = ("materia", "oggi", "settimana", "mese", "totale")
        self.tree_materie = ttk.Treeview(
            subjects_card,
            columns=columns,
            show="headings",
            height=8,
        )

        headings = {
            "materia": "Materia",
            "oggi": "Oggi",
            "settimana": "Settimana",
            "mese": "Mese",
            "totale": "Totale",
        }

        for col in columns:
            self.tree_materie.heading(
                col,
                text=headings[col],
                command=lambda c=col: self._sort_tree_by(c),
            )

        self.tree_materie.column("materia", anchor="w", width=190)
        self.tree_materie.column("oggi", anchor="center", width=100)
        self.tree_materie.column("settimana", anchor="center", width=120)
        self.tree_materie.column("mese", anchor="center", width=100)
        self.tree_materie.column("totale", anchor="center", width=100)

        scrollbar = ttk.Scrollbar(
            subjects_card,
            orient="vertical",
            command=self.tree_materie.yview,
        )
        self.tree_materie.configure(yscrollcommand=scrollbar.set)

        self.tree_materie.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Barra info in basso
        info_bar = ttk.Frame(
            self,
            style="Surface.TFrame",
            padding=(16, 10),
        )
        info_bar.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(18, 0))
        info_bar.columnconfigure(0, weight=1)

        ttk.Label(
            info_bar,
            textvariable=self.var_info,
            anchor="w",
            style="Surface.TLabel",
        ).grid(row=0, column=0, sticky="ew")

        self._update_progress_colors()
        self._apply_tree_styles()

        root = self.winfo_toplevel()
        try:
            root.bind("<<PlannerThemeChanged>>", self._handle_theme_change, add="+")
        except Exception:
            pass

    def _build_stat_box(self, parent, column: int, label: str, variable: tk.StringVar):
        box = ttk.Frame(parent, style="Surface.TFrame", padding=(8, 6))
        box.grid(row=0, column=column, sticky="ew", padx=6)
        box.columnconfigure(0, weight=1)

        ttk.Label(
            box,
            text=label,
            style="SurfaceSubtle.TLabel",
            anchor="center",
        ).grid(row=0, column=0, sticky="ew")

        ttk.Label(
            box,
            textvariable=variable,
            style="Value.TLabel",
            anchor="center",
        ).grid(row=1, column=0, sticky="ew", pady=(4, 0))

    # BOTTONI

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

        if minuti_studio <= 0 or minuti_riposo <= 0:
            messagebox.showwarning("Attenzione!", "Minuti di studio o pausa devono essere superiori a 0.")
            return

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
            self.btn_pause.config(text="Pausa")

            if self.state == "pausa_studio":
                self._switch_to(
                    "studio",
                    seconds=self.sec_restanti,
                    lock_inputs=True,
                    change_buttons=False,
                    reset_target=False,
                )
                self._log("Studio ripreso")
            else:
                self._switch_to(
                    "riposo",
                    seconds=self.sec_restanti,
                    lock_inputs=True,
                    change_buttons=False,
                    reset_target=False,
                )
                self._log("Riposo ripreso")

            self._tick()

    def on_stop(self):
        self._cancel_after()

        if self.state in ("studio", "pausa_studio"):
            sec_fatti = self.sec_target - self.sec_restanti
            minuti_fatti = sec_fatti // 60

            if minuti_fatti >= self.minimo_salvataggio_min:
                self._salva(self.materia_corrente, minuti_fatti)
                self._log(f"Sessione interrotta e salvata ({minuti_fatti} min).")
                self._update_stats()
            else:
                self._log("Interrotto: meno di 1 minuto, non salvo.")
        else:
            self._log("Timer fermato.")

        self._reset_to_idle()

    # TIMER

    def _switch_to(
        self,
        new_state: str,
        seconds: int,
        lock_inputs: bool = True,
        change_buttons: bool = True,
        reset_target: bool = True,
    ):
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

        try:
            studio_seconds = int(self.var_studio.get()) * 60
            self.var_timer.set(fmt_mmss(studio_seconds))
        except Exception:
            self.var_timer.set("25:00")

        self.var_fase.set("Studio")
        self._set_buttons(running=False)
        self._lock_inputs(False)
        self._reset_progress_arc()

    def _reset_after_cycle(self, message: str = "Pronto!"):
        self._reset_to_idle()
        self._log(message)

    def _tick(self):
        self.after_id = None
        self.var_timer.set(fmt_mmss(self.sec_restanti))
        self._update_progress_arc()

        if self.sec_restanti <= 0:
            self._handle_phase_complete()
            return

        self.sec_restanti -= 1
        self.after_id = self.after(1000, self._tick)

    def _handle_phase_complete(self):
        current_state = self.state

        if current_state == "studio":
            minuti_fatti = (self.sec_target // 60) if self.sec_target else 0

            if minuti_fatti >= self.minimo_salvataggio_min:
                self._salva(self.materia_corrente, minuti_fatti)
                self._update_stats()
                self._log(f"Sessione completata ({minuti_fatti} min).")
            else:
                self._log("Sessione troppo breve, non salvo.")

            minuti_riposo = int(self.var_riposo.get())

            if minuti_riposo > 0:
                self._switch_to("riposo", seconds=minuti_riposo * 60)
                self._tick()
            else:
                self._reset_after_cycle("Sessione completata.")

        elif current_state == "riposo":
            self._log("Pausa terminata.")

            if self.var_auto.get():
                minuti_studio = int(self.var_studio.get())

                if minuti_studio > 0:
                    self._switch_to("studio", seconds=minuti_studio * 60)
                    self._tick()
                else:
                    self._reset_after_cycle()
            else:
                self._reset_after_cycle("Pausa terminata. Premi Avvia per continuare.")

        else:
            self._reset_after_cycle()

    # STATO UI

    def _set_buttons(self, running: bool):
        if running:
            self.btn_start.config(state="disabled")
            self.btn_pause.config(state="normal", text="Pausa")
            self.btn_stop.config(state="normal")
        else:
            self.btn_start.config(state="normal")
            self.btn_pause.config(state="disabled", text="Pausa")
            self.btn_stop.config(state="disabled")

    def _lock_inputs(self, locked: bool):
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
        self.var_info.set(msg)

    # SALVATAGGIO

    def _salva(self, materia: str, minuti: int):
        if minuti <= 0:
            return

        oggi = date.today().isoformat()

        self.tempo_studiato.setdefault(materia, [])
        self.tempo_studiato[materia].append(
            {
                "data": oggi,
                "minuti": int(minuti),
            }
        )

        save_data(self.tempo_studiato, FILE_NAME)

    # GRAFICA TIMER

    def _reset_progress_arc(self):
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
        if not hasattr(self, "canvas_timer"):
            return

        palette = getattr(self.winfo_toplevel(), "_planner_palette", None)

        if palette is not None:
            background = palette.surface
            arc_bg = palette.border
            arc_fg = palette.accent
        else:
            background = self._get_timer_background()
            arc_bg = "#E4E7F5"
            arc_fg = "#5465FF"

        self.canvas_timer.configure(bg=background)
        self.canvas_timer.itemconfigure(self.arc_background, outline=arc_bg)
        self.canvas_timer.itemconfigure(self.arc_progress, outline=arc_fg)

    def _handle_theme_change(self, _event=None):
        self._update_progress_colors()
        self._update_progress_arc()
        self._apply_tree_styles()

    def _get_timer_background(self) -> str:
        palette = getattr(self.winfo_toplevel(), "_planner_palette", None)

        if palette is not None:
            return palette.surface

        try:
            return self.winfo_toplevel().cget("background")
        except Exception:
            return "#FFFFFF"

    # STATISTICHE

    def _update_stats(self):
        try:
            oggi = somma(self.tempo_studiato, "oggi")
            settimana = somma(self.tempo_studiato, "settimana")
            mese = somma(self.tempo_studiato, "mese")

            self.var_stat_oggi.set(fmt_mm(oggi))
            self.var_stat_sett.set(fmt_mm(settimana))
            self.var_stat_mese.set(fmt_mm(mese))

            self._update_subject_breakdown()

        except Exception:
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
            odd_bg = "#F4F6FF"
            fg = "#2E3532"

        self.tree_materie.tag_configure("evenrow", background=even_bg, foreground=fg)
        self.tree_materie.tag_configure("oddrow", background=odd_bg, foreground=fg)

    def _update_subject_breakdown(self):
        if self.tree_materie is None:
            return

        self.tree_materie.delete(*self.tree_materie.get_children())

        if not self.tempo_studiato:
            return

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
        if self.tree_materie is None:
            return

        for index, row in enumerate(rows):
            tags = (
                f"raw_{row['materia']}",
                "evenrow" if index % 2 == 0 else "oddrow",
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

            current_rows.append(
                {
                    "materia": materia,
                    "oggi": oggi,
                    "settimana": settimana,
                    "mese": mese,
                    "totale": totale,
                }
            )

        if not current_rows:
            return

        descending = getattr(self, "_sort_desc", {})
        descending[column] = not descending.get(column, False)
        self._sort_desc = descending

        if column == "materia":
            key_fn = lambda row: row["materia"].lower()
        else:
            key_fn = lambda row: row[column]

        ordered = sorted(current_rows, key=key_fn, reverse=descending[column])

        self.tree_materie.delete(*self.tree_materie.get_children())
        self._insert_tree_rows(ordered)


def create_pomodoro_frame(parent):
    return Pomodoro(parent)