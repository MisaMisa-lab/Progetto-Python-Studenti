import math
import tkinter as tk
from datetime import date
from tkinter import messagebox, ttk

from report import fmt_mm, somma
from storage import FILE_NAME, load_data, save_data


def fmt_mmss(seconds: int) -> str:
    seconds = max(0, int(seconds))
    minutes, seconds = divmod(seconds, 60)
    return f"{minutes:02d}:{seconds:02d}"


class Pomodoro(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=0, style="Background.TFrame")

        self.data = load_data(FILE_NAME)

        self.state = "idle"
        self.after_id = None
        self.sec_target = 0
        self.sec_left = 0
        self.current_subject = ""

        self.var_subject = tk.StringVar()
        self.var_study = tk.IntVar(value=25)
        self.var_break = tk.IntVar(value=5)
        self.var_auto = tk.BooleanVar(value=False)

        self.var_timer = tk.StringVar(value="25:00")
        self.var_phase = tk.StringVar(value="Studio")
        self.var_info = tk.StringVar(value="Pronto!")

        self.var_today = tk.StringVar(value="—")
        self.var_week = tk.StringVar(value="—")
        self.var_month = tk.StringVar(value="—")

        self.tree_subjects = None
        self.progress_color = "#5465FF"
        self.track_color = "#E4E7F5"

        self.build_scroll_area()
        self.build_ui()
        self.update_stats()

    def build_scroll_area(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.canvas_scroll = tk.Canvas(self, highlightthickness=0, borderwidth=0)
        self.canvas_scroll.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas_scroll.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.canvas_scroll.configure(yscrollcommand=scrollbar.set)

        self.page = ttk.Frame(self.canvas_scroll, padding=10, style="Background.TFrame")
        self.canvas_window = self.canvas_scroll.create_window((0, 0), window=self.page, anchor="nw")

        self.page.bind("<Configure>", lambda e: self.canvas_scroll.configure(scrollregion=self.canvas_scroll.bbox("all")))
        self.canvas_scroll.bind("<Configure>", lambda e: self.canvas_scroll.itemconfigure(self.canvas_window, width=e.width))

        self.canvas_scroll.bind("<Enter>", lambda e: self.canvas_scroll.bind_all("<MouseWheel>", self.on_mousewheel))
        self.canvas_scroll.bind("<Leave>", lambda e: self.canvas_scroll.unbind_all("<MouseWheel>"))

    def on_mousewheel(self, event):
        self.canvas_scroll.yview_scroll(int(-event.delta / 120), "units")

    def build_ui(self):
        page = self.page
        page.columnconfigure(0, weight=4)
        page.columnconfigure(1, weight=6)
        page.rowconfigure(1, weight=1)

        left = ttk.Frame(page, style="Background.TFrame")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left.columnconfigure(0, weight=1)

        self.build_settings(left)
        self.build_stats(left)
        self.build_timer(page)
        self.build_subject_table(page)

        self.update_timer_colors()

        try:
            self.winfo_toplevel().bind("<<PlannerThemeChanged>>", self.on_theme_change, add="+")
        except Exception:
            pass

    def build_settings(self, parent):
        frame = ttk.LabelFrame(parent, text="Impostazioni", style="Surface.TLabelframe")
        frame.grid(row=0, column=0, sticky="ew")
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(3, weight=1)

        ttk.Label(frame, text="Materia", style="Surface.TLabel").grid(row=0, column=0, sticky="w", padx=(2, 8), pady=6)
        ttk.Entry(frame, textvariable=self.var_subject).grid(row=0, column=1, columnspan=3, sticky="ew", pady=6)

        ttk.Label(frame, text="Studio", style="Surface.TLabel").grid(row=1, column=0, sticky="w", padx=(2, 8), pady=6)
        ttk.Spinbox(frame, from_=1, to=240, textvariable=self.var_study, width=6).grid(row=1, column=1, sticky="w", pady=6)

        ttk.Label(frame, text="Pausa", style="Surface.TLabel").grid(row=1, column=2, sticky="w", padx=(14, 8), pady=6)
        ttk.Spinbox(frame, from_=1, to=120, textvariable=self.var_break, width=6).grid(row=1, column=3, sticky="w", pady=6)

        ttk.Checkbutton(
            frame,
            text="Auto-continua",
            variable=self.var_auto,
            style="Surface.TCheckbutton",
        ).grid(row=2, column=0, columnspan=4, sticky="w", pady=(6, 2))

    def build_stats(self, parent):
        frame = ttk.LabelFrame(parent, text="Statistiche", style="Surface.TLabelframe")
        frame.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        frame.columnconfigure(0, weight=1)

        self.stat_row(frame, 0, "Oggi", self.var_today)
        self.separator(frame, 1)
        self.stat_row(frame, 2, "Settimana", self.var_week)
        self.separator(frame, 3)
        self.stat_row(frame, 4, "Mese", self.var_month)

    def stat_row(self, parent, row: int, label: str, variable: tk.StringVar):
        frame = ttk.Frame(parent, style="Surface.TFrame", padding=(0, 4))
        frame.grid(row=row, column=0, sticky="ew")
        frame.columnconfigure(0, weight=1)

        ttk.Label(frame, text=label, style="Surface.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(frame, textvariable=variable, style="Value.TLabel").grid(row=0, column=1, sticky="e")

    def separator(self, parent, row: int):
        ttk.Separator(parent, orient="horizontal").grid(row=row, column=0, sticky="ew")

    def build_timer(self, parent):
        frame = ttk.LabelFrame(parent, text="", style="Surface.TLabelframe")
        frame.grid(row=0, column=1, sticky="nsew")
        frame.columnconfigure(0, weight=1)

        ttk.Label(frame, textvariable=self.var_info, style="Value.TLabel", anchor="center").grid(row=0, column=0, pady=(2, 0))
        ttk.Label(frame, text="—", style="SurfaceSubtle.TLabel", anchor="center").grid(row=1, column=0)

        area = ttk.Frame(frame, style="Surface.TFrame")
        area.grid(row=2, column=0)

        self.canvas_timer = tk.Canvas(area, width=210, height=210, highlightthickness=0)
        self.canvas_timer.grid(row=0, column=0)

        self.track = self.canvas_timer.create_oval(18, 18, 192, 192, outline=self.track_color, width=12)
        self.progress_items = []

        ttk.Label(area, textvariable=self.var_timer, font=("Inter", 30, "bold"), style="Surface.TLabel").place(
            in_=self.canvas_timer,
            relx=0.5,
            rely=0.45,
            anchor="center",
        )

        ttk.Label(area, textvariable=self.var_phase, font=("Inter", 11, "bold"), style="Value.TLabel").place(
            in_=self.canvas_timer,
            relx=0.5,
            rely=0.61,
            anchor="center",
        )

        buttons = ttk.Frame(frame, style="Surface.TFrame")
        buttons.grid(row=3, column=0, sticky="ew", padx=10, pady=(4, 8))

        for col in range(3):
            buttons.columnconfigure(col, weight=1)

        self.btn_start = ttk.Button(buttons, text="Avvia", command=self.start, style="Primary.TButton")
        self.btn_start.grid(row=0, column=0, sticky="ew", padx=(0, 4))

        self.btn_pause = ttk.Button(buttons, text="Pausa", command=self.pause, state="disabled")
        self.btn_pause.grid(row=0, column=1, sticky="ew", padx=4)

        self.btn_stop = ttk.Button(buttons, text="Stop", command=self.stop, state="disabled")
        self.btn_stop.grid(row=0, column=2, sticky="ew", padx=(4, 0))

        ttk.Label(
            frame,
            textvariable=self.var_info,
            style="SurfaceSubtle.TLabel",
            anchor="center",
        ).grid(row=4, column=0, sticky="ew", padx=10, pady=(0, 4))

    def build_subject_table(self, parent):
        frame = ttk.LabelFrame(parent, text="Dettaglio materie", style="Surface.TLabelframe")
        frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(10, 0))
        frame.columnconfigure(0, weight=1)

        columns = ("materia", "oggi", "settimana", "mese", "totale")
        self.tree_subjects = ttk.Treeview(frame, columns=columns, show="headings", height=4)

        for col, title in zip(columns, ("Materia", "Oggi", "Settimana", "Mese", "Totale")):
            self.tree_subjects.heading(col, text=title, command=lambda c=col: self.sort_table(c))

        self.tree_subjects.column("materia", anchor="w", width=220)
        for col in columns[1:]:
            self.tree_subjects.column(col, anchor="center", width=100)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree_subjects.yview)
        self.tree_subjects.configure(yscrollcommand=scrollbar.set)

        self.tree_subjects.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

    def start(self):
        subject = self.var_subject.get().strip().lower()

        if not subject:
            messagebox.showwarning("Attenzione", "Inserisci una materia.")
            return

        try:
            study = int(self.var_study.get())
            pause = int(self.var_break.get())
        except (tk.TclError, ValueError):
            messagebox.showwarning("Attenzione", "Inserisci minuti validi.")
            return

        if study <= 0 or pause <= 0:
            messagebox.showwarning("Attenzione", "I minuti devono essere maggiori di 0.")
            return

        self.current_subject = subject
        self.var_subject.set(subject)

        self.switch_to("studio", study * 60)
        self.var_info.set("Sessione avviata")
        self.tick()

    def pause(self):
        if self.state == "studio":
            self.cancel_timer()
            self.state = "pause_study"
            self.var_phase.set("Pausa")
            self.btn_pause.config(text="Riprendi")
            self.var_info.set("Studio in pausa")

        elif self.state == "riposo":
            self.cancel_timer()
            self.state = "pause_break"
            self.var_phase.set("Pausa")
            self.btn_pause.config(text="Riprendi")
            self.var_info.set("Riposo in pausa")

        elif self.state in ("pause_study", "pause_break"):
            new_state = "studio" if self.state == "pause_study" else "riposo"
            self.switch_to(new_state, self.sec_left, change_buttons=False, reset_target=False)
            self.btn_pause.config(text="Pausa")
            self.var_info.set("Timer ripreso")
            self.tick()

    def stop(self):
        self.cancel_timer()

        if self.state in ("studio", "pause_study"):
            studied = (self.sec_target - self.sec_left) // 60

            if studied >= 1:
                self.save_session(self.current_subject, studied)
                self.var_info.set(f"Salvato: {studied} min")
                self.update_stats()
            else:
                self.var_info.set("Meno di 1 minuto, non salvo")
        else:
            self.var_info.set("Timer fermato")

        self.reset()

    def switch_to(self, state: str, seconds: int, change_buttons: bool = True, reset_target: bool = True):
        self.cancel_timer()

        self.state = state
        self.sec_left = int(seconds)

        if reset_target:
            self.sec_target = int(seconds)

        self.var_timer.set(fmt_mmss(self.sec_left))
        self.var_phase.set("Studio" if state == "studio" else "Riposo")

        if change_buttons:
            self.set_running(True)

        self.lock_inputs(True)
        self.update_progress()

    def reset(self):
        self.cancel_timer()

        self.state = "idle"
        self.sec_target = 0
        self.sec_left = 0

        try:
            self.var_timer.set(fmt_mmss(int(self.var_study.get()) * 60))
        except Exception:
            self.var_timer.set("25:00")

        self.var_phase.set("Studio")
        self.set_running(False)
        self.lock_inputs(False)
        self.update_progress()

    def tick(self):
        self.var_timer.set(fmt_mmss(self.sec_left))
        self.update_progress()

        if self.sec_left <= 0:
            self.complete_phase()
            return

        self.sec_left -= 1
        self.after_id = self.after(1000, self.tick)

    def complete_phase(self):
        if self.state == "studio":
            minutes = self.sec_target // 60
            self.save_session(self.current_subject, minutes)
            self.update_stats()
            self.var_info.set(f"Sessione completata: {minutes} min")

            self.switch_to("riposo", int(self.var_break.get()) * 60)
            self.tick()

        elif self.state == "riposo":
            if self.var_auto.get():
                self.switch_to("studio", int(self.var_study.get()) * 60)
                self.tick()
            else:
                self.reset()
                self.var_info.set("Pausa terminata")

    def set_running(self, running: bool):
        self.btn_start.config(state="disabled" if running else "normal")
        self.btn_pause.config(state="normal" if running else "disabled", text="Pausa")
        self.btn_stop.config(state="normal" if running else "disabled")

    def lock_inputs(self, locked: bool):
        state = "disabled" if locked else "normal"

        def visit(widget):
            if isinstance(widget, (ttk.Entry, ttk.Spinbox, ttk.Checkbutton)):
                try:
                    widget.configure(state=state)
                except tk.TclError:
                    pass

            for child in widget.winfo_children():
                visit(child)

        visit(self.page)

    def cancel_timer(self):
        if self.after_id:
            try:
                self.after_cancel(self.after_id)
            except Exception:
                pass

        self.after_id = None

    def save_session(self, subject: str, minutes: int):
        if minutes <= 0:
            return

        today = date.today().isoformat()
        self.data.setdefault(subject, [])
        self.data[subject].append({"data": today, "minuti": int(minutes)})
        save_data(self.data, FILE_NAME)

    def update_stats(self):
        try:
            self.var_today.set(fmt_mm(somma(self.data, "oggi")))
            self.var_week.set(fmt_mm(somma(self.data, "settimana")))
            self.var_month.set(fmt_mm(somma(self.data, "mese")))
            self.update_subject_table()
        except Exception:
            self.var_today.set("—")
            self.var_week.set("—")
            self.var_month.set("—")

    def update_subject_table(self):
        self.tree_subjects.delete(*self.tree_subjects.get_children())

        rows = []

        for subject, sessions in self.data.items():
            single = {subject: sessions}
            today = somma(single, "oggi")
            week = somma(single, "settimana")
            month = somma(single, "mese")
            total = sum(int(item.get("minuti", 0)) for item in sessions)
            rows.append((subject, today, week, month, total))

        self.insert_rows(rows)

    def insert_rows(self, rows):
        for index, row in enumerate(rows):
            tag = "evenrow" if index % 2 == 0 else "oddrow"

            self.tree_subjects.insert(
                "",
                "end",
                values=(row[0].capitalize(), fmt_mm(row[1]), fmt_mm(row[2]), fmt_mm(row[3]), fmt_mm(row[4])),
                tags=(tag,),
            )

        self.apply_tree_style()

    def sort_table(self, column: str):
        index_map = {"materia": 0, "oggi": 1, "settimana": 2, "mese": 3, "totale": 4}
        rows = []

        for subject, sessions in self.data.items():
            single = {subject: sessions}
            rows.append((
                subject,
                somma(single, "oggi"),
                somma(single, "settimana"),
                somma(single, "mese"),
                sum(int(item.get("minuti", 0)) for item in sessions),
            ))

        reverse = getattr(self, "sort_reverse", False)
        self.sort_reverse = not reverse
        rows.sort(key=lambda row: row[index_map[column]], reverse=reverse)

        self.tree_subjects.delete(*self.tree_subjects.get_children())
        self.insert_rows(rows)

    def update_progress(self):
        if self.sec_target <= 0:
            percent = 0.18
        else:
            percent = (self.sec_target - self.sec_left) / self.sec_target
            percent = max(0.01, min(1, percent))

        self.draw_round_arc(percent)

    def draw_round_arc(self, percent: float):
        for item in self.progress_items:
            self.canvas_timer.delete(item)

        self.progress_items.clear()

        cx, cy = 105, 105
        radius = 87
        start_angle = -90
        end_angle = start_angle + (360 * percent)
        steps = max(4, int(80 * percent))

        points = []

        for i in range(steps + 1):
            angle = start_angle + (end_angle - start_angle) * i / steps
            rad = math.radians(angle)
            x = cx + radius * math.cos(rad)
            y = cy + radius * math.sin(rad)
            points.extend((x, y))

        arc = self.canvas_timer.create_line(
            *points,
            fill=self.progress_color,
            width=12,
            capstyle=tk.ROUND,
            joinstyle=tk.ROUND,
            smooth=True,
        )

        self.progress_items.append(arc)

    def update_timer_colors(self):
        palette = getattr(self.winfo_toplevel(), "_planner_palette", None)

        if palette:
            self.progress_color = palette.accent
            self.track_color = palette.border

            self.canvas_timer.configure(bg=palette.surface)
            self.canvas_scroll.configure(bg=palette.base)
            self.canvas_timer.itemconfigure(self.track, outline=self.track_color)

        self.update_progress()

    def apply_tree_style(self):
        palette = getattr(self.winfo_toplevel(), "_planner_palette", None)

        even = palette.surface if palette else "#FFFFFF"
        odd = palette.alternate if palette else "#F4F6FF"
        text = palette.text if palette else "#2E3532"

        self.tree_subjects.tag_configure("evenrow", background=even, foreground=text)
        self.tree_subjects.tag_configure("oddrow", background=odd, foreground=text)

    def on_theme_change(self, _event=None):
        self.update_timer_colors()
        self.apply_tree_style()


def create_pomodoro_frame(parent):
    return Pomodoro(parent)