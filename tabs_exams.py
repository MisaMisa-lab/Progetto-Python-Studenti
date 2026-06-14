import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List

from logic_exams import (
    add_exam,
    calculate_averages,
    format_grade,
    load_exams_data,
    remove_exam,
    sort_exams,
)


class ExamsTab(ttk.Frame):
    def __init__(self, parent: tk.Widget):
        super().__init__(parent, padding=14, style="Background.TFrame")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self.exams: List[Dict[str, float]] = load_exams_data()

        self.var_avg = tk.StringVar(value="—")
        self.var_weighted = tk.StringVar(value="—")

        self.build_ui()
        self.refresh_table()
        self.update_stats()
        self.apply_tree_style()

        try:
            self.winfo_toplevel().bind("<<PlannerThemeChanged>>", self.on_theme_change, add="+")
        except Exception:
            pass

    def build_ui(self):
        self.build_form()
        self.build_table()
        self.build_summary()

    def build_form(self):
        form = ttk.LabelFrame(self, text="Nuovo esame", style="Surface.TLabelframe")
        form.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        form.columnconfigure(0, weight=3)
        form.columnconfigure(1, weight=1)
        form.columnconfigure(2, weight=1)
        form.columnconfigure(3, weight=2)

        ttk.Label(form, text="Materia", style="Surface.TLabel").grid(row=0, column=0, sticky="w", padx=(2, 8), pady=(4, 2))
        ttk.Label(form, text="CFU", style="Surface.TLabel").grid(row=0, column=1, sticky="w", padx=(12, 8), pady=(4, 2))
        ttk.Label(form, text="Voto", style="Surface.TLabel").grid(row=0, column=2, sticky="w", padx=(12, 8), pady=(4, 2))

        self.entry_subject = ttk.Entry(form)
        self.entry_subject.grid(row=1, column=0, sticky="ew", padx=(2, 8), pady=(0, 4))

        self.entry_cfu = ttk.Entry(form)
        self.entry_cfu.grid(row=1, column=1, sticky="ew", padx=(12, 8), pady=(0, 4))

        self.entry_grade = ttk.Entry(form)
        self.entry_grade.grid(row=1, column=2, sticky="ew", padx=(12, 8), pady=(0, 4))

        ttk.Button(
            form,
            text="Aggiungi",
            command=self.add_exam_from_form,
            style="Primary.TButton",
        ).grid(row=1, column=3, sticky="ew", padx=(20, 2), pady=(0, 4))

    def build_table(self):
        frame = ttk.LabelFrame(self, text="Esami registrati", style="Surface.TLabelframe")
        frame.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        columns = ("subject", "cfu", "grade")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings", height=7)

        self.tree.heading("subject", text="Materia", command=lambda: self.sort_by("subject"))
        self.tree.heading("cfu", text="CFU", command=lambda: self.sort_by("cfu"))
        self.tree.heading("grade", text="Voto", command=lambda: self.sort_by("grade"))

        self.tree.column("subject", anchor="w", width=420)
        self.tree.column("cfu", anchor="center", width=100)
        self.tree.column("grade", anchor="center", width=100)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        bottom = ttk.Frame(frame, style="Surface.TFrame")
        bottom.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        bottom.columnconfigure(0, weight=1)

        ttk.Label(
            bottom,
            text="Clicca sulle intestazioni per ordinare.",
            style="SurfaceSubtle.TLabel",
        ).grid(row=0, column=0, sticky="w")

        ttk.Button(
            bottom,
            text="Rimuovi selezionato",
            command=self.remove_selected,
        ).grid(row=0, column=1, sticky="e")

    def build_summary(self):
        frame = ttk.LabelFrame(self, text="Riepilogo medie", style="Surface.TLabelframe")
        frame.grid(row=2, column=0, sticky="ew")
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

        self.average_card(frame, 0, "Media aritmetica", self.var_avg)
        self.average_card(frame, 1, "Media ponderata", self.var_weighted)

    def average_card(self, parent, column: int, label: str, variable: tk.StringVar):
        frame = ttk.Frame(parent, style="Surface.TFrame", padding=(10, 6))
        frame.grid(row=0, column=column, sticky="ew", padx=(0, 6) if column == 0 else (6, 0))
        frame.columnconfigure(0, weight=1)

        ttk.Label(frame, text=label, style="SurfaceSubtle.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(frame, textvariable=variable, style="Value.TLabel").grid(row=1, column=0, sticky="w")

    def add_exam_from_form(self):
        subject = self.entry_subject.get()
        cfu = self.entry_cfu.get()
        grade = self.entry_grade.get()

        try:
            add_exam(self.exams, subject, cfu, grade)
        except ValueError as error:
            messagebox.showwarning("Attenzione", str(error))
            return

        self.refresh_table()
        self.update_stats()

        self.entry_subject.delete(0, tk.END)
        self.entry_cfu.delete(0, tk.END)
        self.entry_grade.delete(0, tk.END)

    def refresh_table(self):
        self.tree.delete(*self.tree.get_children())

        for index, exam in enumerate(self.exams):
            tag = "evenrow" if index % 2 == 0 else "oddrow"

            self.tree.insert(
                "",
                "end",
                values=(exam["subject"], exam["cfu"], format_grade(exam["grade"])),
                tags=(tag,),
            )

        self.apply_tree_style()

    def update_stats(self):
        average, weighted = calculate_averages(self.exams)

        self.var_avg.set(average)
        self.var_weighted.set(weighted)

    def sort_by(self, column: str):
        if not hasattr(self, "sort_state"):
            self.sort_state = {}

        reverse = not self.sort_state.get(column, False)
        self.sort_state[column] = reverse

        sort_exams(self.exams, column, reverse)
        self.refresh_table()

    def remove_selected(self):
        selection = self.tree.selection()

        if not selection:
            messagebox.showinfo("Seleziona un esame", "Seleziona un esame da rimuovere.")
            return

        subject, cfu, grade = self.tree.item(selection[0], "values")

        if not messagebox.askyesno("Conferma rimozione", f"Vuoi eliminare '{subject}'?"):
            return

        removed = remove_exam(self.exams, subject, cfu, grade)

        if removed:
            self.refresh_table()
            self.update_stats()
        else:
            messagebox.showwarning("Errore", "Esame non trovato.")

    def apply_tree_style(self):
        palette = getattr(self.winfo_toplevel(), "_planner_palette", None)

        even = palette.surface if palette else "#FFFFFF"
        odd = palette.alternate if palette else "#F4F6FF"
        text = palette.text if palette else "#2E3532"

        self.tree.tag_configure("evenrow", background=even, foreground=text)
        self.tree.tag_configure("oddrow", background=odd, foreground=text)

    def on_theme_change(self, _event=None):
        self.apply_tree_style()


def create_exams_tab(parent: tk.Widget) -> ttk.Frame:
    return ExamsTab(parent)