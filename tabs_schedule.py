import tkinter as tk
from tkinter import ttk, messagebox

from logic_schedule import (
    DAYS,
    REPEAT_OPTIONS,
    add_activity,
    get_current_day_index,
    get_date_for_day,
    get_date_text,
    get_day_entries,
    get_week_start,
    load_schedule_data,
    remove_activity,
    sort_activities,
)


class ScheduleTab(ttk.Frame):
    def __init__(self, parent: tk.Widget):
        super().__init__(parent, padding=14, style="Background.TFrame")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        self.schedule = load_schedule_data()
        self.week_start = get_week_start()
        self.current_day = get_current_day_index()

        self.var_day = tk.StringVar()
        self.var_date = tk.StringVar()
        self.var_hint = tk.StringVar()

        self.build_ui()
        self.refresh_day()
        self.apply_tree_style()

        try:
            self.winfo_toplevel().bind("<<PlannerThemeChanged>>", self.on_theme_change, add="+")
        except Exception:
            pass

    def build_ui(self):
        self.build_navigation()
        self.build_form()
        self.build_table()

    def build_navigation(self):
        nav = ttk.Frame(self, style="Background.TFrame")
        nav.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        nav.columnconfigure(1, weight=1)

        self.btn_prev = ttk.Button(nav, text="‹", width=3, command=self.previous_day)
        self.btn_prev.grid(row=0, column=0, sticky="w")

        center = ttk.Frame(nav, style="Background.TFrame")
        center.grid(row=0, column=1)

        ttk.Label(
            center,
            textvariable=self.var_day,
            style="Subtle.TLabel",
            font=("Poppins", 15, "bold"),
        ).grid(row=0, column=0)

        ttk.Label(
            center,
            textvariable=self.var_date,
            style="Subtle.TLabel",
        ).grid(row=1, column=0, pady=(2, 0))

        self.btn_next = ttk.Button(nav, text="›", width=3, command=self.next_day)
        self.btn_next.grid(row=0, column=2, sticky="e")

    def build_form(self):
        form = ttk.LabelFrame(self, text="Aggiungi attività", style="Surface.TLabelframe")
        form.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        form.columnconfigure(1, weight=1)
        form.columnconfigure(3, weight=1)
        form.columnconfigure(5, weight=1)

        ttk.Label(form, text="Giorno", style="Surface.TLabel").grid(
            row=0,
            column=0,
            sticky="w",
            padx=(2, 8),
            pady=6,
        )

        self.combo_day = ttk.Combobox(form, values=DAYS, state="readonly", style="Planner.TCombobox")
        self.combo_day.grid(row=0, column=1, sticky="ew", pady=6)

        ttk.Label(form, text="Orario", style="Surface.TLabel").grid(
            row=0,
            column=2,
            sticky="w",
            padx=(14, 8),
            pady=6,
        )

        self.entry_time = ttk.Entry(form)
        self.entry_time.grid(row=0, column=3, sticky="ew", pady=6)

        ttk.Label(form, text="Ripeti", style="Surface.TLabel").grid(
            row=0,
            column=4,
            sticky="w",
            padx=(14, 8),
            pady=6,
        )

        self.combo_repeat = ttk.Combobox(form, values=REPEAT_OPTIONS, state="readonly", style="Planner.TCombobox")
        self.combo_repeat.current(0)
        self.combo_repeat.grid(row=0, column=5, sticky="ew", pady=6)

        ttk.Label(form, text="Attività", style="Surface.TLabel").grid(
            row=1,
            column=0,
            sticky="w",
            padx=(2, 8),
            pady=6,
        )

        self.entry_subject = ttk.Entry(form)
        self.entry_subject.grid(row=1, column=1, columnspan=2, sticky="ew", pady=6)

        ttk.Label(form, text="Note", style="Surface.TLabel").grid(
            row=1,
            column=3,
            sticky="w",
            padx=(14, 8),
            pady=6,
        )

        self.entry_notes = ttk.Entry(form)
        self.entry_notes.grid(row=1, column=4, columnspan=2, sticky="ew", pady=6)

        ttk.Button(
            form,
            text="Aggiungi",
            command=self.add_activity_from_form,
            style="Primary.TButton",
        ).grid(row=2, column=5, sticky="e", pady=(6, 2))

    def build_table(self):
        frame = ttk.LabelFrame(self, text="Attività del giorno", style="Surface.TLabelframe")
        frame.grid(row=2, column=0, sticky="nsew")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        columns = ("time", "subject", "repeat", "notes")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings", height=7)

        self.tree.heading("time", text="Orario", command=lambda: self.sort_by("time"))
        self.tree.heading("subject", text="Attività", command=lambda: self.sort_by("subject"))
        self.tree.heading("repeat", text="Ripeti", command=lambda: self.sort_by("repeat"))
        self.tree.heading("notes", text="Note", command=lambda: self.sort_by("notes"))

        self.tree.column("time", anchor="center", width=90)
        self.tree.column("subject", anchor="w", width=240)
        self.tree.column("repeat", anchor="center", width=140)
        self.tree.column("notes", anchor="w", width=240)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        bottom = ttk.Frame(frame, style="Surface.TFrame")
        bottom.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        bottom.columnconfigure(0, weight=1)

        ttk.Label(
            bottom,
            textvariable=self.var_hint,
            style="SurfaceSubtle.TLabel",
        ).grid(row=0, column=0, sticky="w")

        ttk.Button(
            bottom,
            text="Rimuovi selezionato",
            command=self.remove_selected,
        ).grid(row=0, column=1, sticky="e")

    def previous_day(self):
        if self.current_day > 0:
            self.current_day -= 1
            self.refresh_day()

    def next_day(self):
        if self.current_day < len(DAYS) - 1:
            self.current_day += 1
            self.refresh_day()

    def refresh_day(self):
        day = DAYS[self.current_day]
        current_date = get_date_for_day(self.week_start, self.current_day)

        self.var_day.set(day)
        self.var_date.set(get_date_text(self.week_start, self.current_day))
        self.combo_day.current(self.current_day)

        self.btn_prev.state(["disabled"] if self.current_day == 0 else ["!disabled"])
        self.btn_next.state(["disabled"] if self.current_day == len(DAYS) - 1 else ["!disabled"])

        self.tree.delete(*self.tree.get_children())

        entries = get_day_entries(self.schedule, day, current_date)

        for index, item in enumerate(entries):
            tag = "evenrow" if index % 2 == 0 else "oddrow"

            self.tree.insert(
                "",
                "end",
                values=(
                    item.get("time", ""),
                    item.get("subject", ""),
                    item.get("repeat", "Ogni settimana"),
                    item.get("notes", ""),
                ),
                tags=(tag,),
            )

        if entries:
            self.var_hint.set(f"{len(entries)} attività pianificate per {day}.")
        else:
            self.var_hint.set(f"Nessuna attività programmata per {day}.")

        self.apply_tree_style()

    def add_activity_from_form(self):
        day = self.combo_day.get()
        time = self.entry_time.get()
        subject = self.entry_subject.get()
        notes = self.entry_notes.get()
        repeat = self.combo_repeat.get()

        day_index = DAYS.index(day)
        activity_date = get_date_for_day(self.week_start, day_index)

        try:
            add_activity(self.schedule, day, time, subject, notes, repeat, activity_date)
        except ValueError as error:
            messagebox.showwarning("Attenzione", str(error))
            return

        if day == DAYS[self.current_day]:
            self.refresh_day()

        self.entry_time.delete(0, tk.END)
        self.entry_subject.delete(0, tk.END)
        self.entry_notes.delete(0, tk.END)
        self.combo_repeat.current(0)

    def remove_selected(self):
        selection = self.tree.selection()

        if not selection:
            messagebox.showinfo("Seleziona un'attività", "Seleziona un'attività da rimuovere.")
            return

        values = self.tree.item(selection[0], "values")

        if not values or len(values) < 4:
            messagebox.showwarning("Errore", "Attività non valida.")
            return

        time, subject, repeat, notes = values
        day = DAYS[self.current_day]

        confirmed = messagebox.askyesno(
            "Conferma eliminazione",
            f"Vuoi eliminare l'attività '{subject}' delle {time}?",
        )

        if not confirmed:
            return

        removed = remove_activity(self.schedule, day, time, subject, repeat, notes)

        if removed:
            self.refresh_day()
        else:
            messagebox.showwarning("Errore", "Attività non trovata.")

    def sort_by(self, column: str):
        day = DAYS[self.current_day]

        if not hasattr(self, "sort_state"):
            self.sort_state = {}

        reverse = not self.sort_state.get(column, False)
        self.sort_state[column] = reverse

        sort_activities(self.schedule, day, column, reverse)
        self.refresh_day()

    def apply_tree_style(self):
        palette = getattr(self.winfo_toplevel(), "_planner_palette", None)

        even = palette.surface if palette else "#FFFFFF"
        odd = palette.alternate if palette else "#F4F6FF"
        text = palette.text if palette else "#2E3532"

        self.tree.tag_configure("evenrow", background=even, foreground=text)
        self.tree.tag_configure("oddrow", background=odd, foreground=text)

    def on_theme_change(self, _event=None):
        self.apply_tree_style()


def create_schedule_tab(parent: tk.Widget) -> ttk.Frame:
    return ScheduleTab(parent)