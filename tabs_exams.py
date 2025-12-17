import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict

from exam_storage import load_exams, save_exams

# Definisce una tab (pannello) per la sezione "Esami", ereditando da ttk.Frame
class ExamsTab(ttk.Frame):
    def __init__(self, parent: tk.Widget):
        super().__init__(parent, padding=16, style="Background.TFrame") # Inizializza il Frame con padding e stile custom
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        self.exams: List[Dict[str, float]] = load_exams() # Carica da disco la lista di esami (ognuno è un dict)

        self._build_ui() # Crea tutti i widget dell’interfaccia
        self._refresh_table() # Popola la tabella con gli esami caricati
        self._update_stats() # Calcola e mostra le medie
        self._apply_tree_styles() # Applica colori alternati alle righe in base al tema (per uno stile un po piu carino)


        try: #controllo tema
            self.winfo_toplevel().bind("<<PlannerThemeChanged>>", self._on_theme_change, add="+")
        except Exception:
            pass

    def _build_ui(self):

        header = ttk.Frame(self, style="Surface.TFrame", padding=(16, 14))# HEADER (titolo + sottotitolo)
        header.grid(row=0, column=0, sticky="ew") 
        header.columnconfigure(0, weight=1)

        ttk.Label(header, text="Esami", style="AppTitle.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(
            header,
            text="Inserisci gli esami, registra CFU e aggiorna velocemente le tue medie.",
            style="SurfaceSubtle.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(6, 0))

        form = ttk.LabelFrame(self, text="Nuovo esame", style="Surface.TLabelframe") # FORM DI INSERIMENTO
        form.grid(row=1, column=0, sticky="ew", pady=(0, 16))
        for col in range(6):
            weight = 1 if col in (1, 3, 5) else 0 # Rende elastiche le colonne dei campi di input
            form.columnconfigure(col, weight=weight)

        ttk.Label(form, text="Materia:", style="SurfaceSubtle.TLabel").grid(row=0, column=0, sticky="w", padx=(6, 0), pady=6)
        self.entry_subject = ttk.Entry(form) # Campo testo per il nome dell’esame/materia
        self.entry_subject.grid(row=0, column=1, sticky="ew", pady=6)

        ttk.Label(form, text="CFU:", style="SurfaceSubtle.TLabel").grid(row=0, column=2, sticky="w", padx=(12, 0), pady=6)
        self.entry_cfu = ttk.Entry(form, width=6) # Campo corto per i CFU
        self.entry_cfu.grid(row=0, column=3, sticky="w", pady=6)

        ttk.Label(form, text="Voto:", style="SurfaceSubtle.TLabel").grid(row=0, column=4, sticky="w", padx=(12, 0), pady=6)
        self.entry_grade = ttk.Entry(form, width=6)  # Campo corto per il voto (decimale ok)
        self.entry_grade.grid(row=0, column=5, sticky="w", pady=6)

        self.btn_add = ttk.Button(form, text="Aggiungi esame", command=self._add_exam, style="Primary.TButton")
        self.btn_add.grid(row=1, column=0, columnspan=6, sticky="e", padx=6, pady=(8, 6))

        table_frame = ttk.LabelFrame(self, text="Esami registrati", style="Surface.TLabelframe") # TABELLA (Treeview) + SCROLLBAR
        table_frame.grid(row=2, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        columns = ("subject", "cfu", "grade") # Definisce le tre colonne logiche
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=8) 
        self.tree.heading("subject", text="Materia", command=lambda: self._sort_by("subject")) # Click = ordina per materia
        self.tree.heading("cfu", text="CFU", command=lambda: self._sort_by("cfu")) # Click = ordina per CFU
        self.tree.heading("grade", text="Voto", command=lambda: self._sort_by("grade")) # Click = ordina per voto

        self.tree.column("subject", anchor="w", width=220) # anchor="w" = testo allineato a sinistra (west)
        self.tree.column("cfu", anchor="center", width=80)
        self.tree.column("grade", anchor="center", width=80)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set) # Collega la scrollbar alla treeview

        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        actions = ttk.Frame(table_frame, style="Surface.TFrame") #rimozione
        actions.grid(row=1, column=0, columnspan=2, sticky="e", pady=(8, 0))
        # Così posso ripulire rapidamente le prove vecchie quando cambiano programmi o CFU
        ttk.Button(actions, text="Rimuovi esame selezionato", command=self._remove_selected_exam).pack(anchor="e")

        stats_frame = ttk.LabelFrame(self, text="Medie", style="Surface.TLabelframe") #box delle medie
        stats_frame.grid(row=3, column=0, sticky="ew", pady=(16, 0))
        stats_frame.columnconfigure(1, weight=1)

        ttk.Label(stats_frame, text="Media aritmetica:", style="SurfaceSubtle.TLabel").grid(row=0, column=0, sticky="w", padx=6, pady=6)
        self.var_avg = tk.StringVar(value="—")
        ttk.Label(stats_frame, textvariable=self.var_avg, style="Surface.TLabel").grid(row=0, column=1, sticky="w", pady=6)

        ttk.Label(stats_frame, text="Media ponderata:", style="SurfaceSubtle.TLabel").grid(row=1, column=0, sticky="w", padx=6, pady=(0, 6))
        self.var_weighted = tk.StringVar(value="—")
        ttk.Label(stats_frame, textvariable=self.var_weighted, style="Surface.TLabel").grid(row=1, column=1, sticky="w", pady=(0, 6))

    def _add_exam(self):
        subject = self.entry_subject.get().strip()
        cfu_raw = self.entry_cfu.get().strip()
        grade_raw = self.entry_grade.get().strip()

        if not subject or not cfu_raw or not grade_raw: 
            messagebox.showwarning("Campi obbligatori", "Compila materia, CFU e voto.") # Validazione: tutti i campi obbligatori
            return
        
        #Controlli inserimento
        try:
            cfu = int(cfu_raw)
            if cfu <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("CFU non valido", "Inserisci un numero intero positivo per i CFU.")
            return

        try:
            grade = float(grade_raw.replace(",", "."))
        except ValueError:
            messagebox.showwarning("Voto non valido", "Inserisci un numero per il voto (es. 28 o 28.5).")
            return

        if not (0 <= grade <= 30):
            messagebox.showwarning("Voto fuori scala", "Il voto deve essere compreso tra 0 e 30.")
            return

        exam = { # Crea il record d’esame
            "subject": subject,
            "cfu": cfu,
            "grade": grade,
        }
        self.exams.append(exam) # Lo aggiunge alla lista in memoria
        self._persist_data() # Salva subito su disco
        self._refresh_table() # Aggiorna la tabella
        self._update_stats() # Ricalcola le medie

        self.entry_subject.delete(0, tk.END)   # Ripulisce i campi e rimette il focus su "Materia"
        self.entry_cfu.delete(0, tk.END)
        self.entry_grade.delete(0, tk.END)
        self.entry_subject.focus_set()

    def _refresh_table(self):
        # Ricostruisco la tabella a ogni modifica per tenere allineati sorting e alternanza righe
        for row in self.tree.get_children():
            self.tree.delete(row)

        for index, exam in enumerate(self.exams):
            tag = "evenrow" if index % 2 == 0 else "oddrow" # Alterna lo sfondo riga
            self.tree.insert(
                "",
                "end",
                values=(exam["subject"], exam["cfu"], f"{exam['grade']:.1f}"), # Mostra voto con 1 decimale
                tags=(tag,),
            )
        self._apply_tree_styles() # Re-applica i colori in base al tema

    def _update_stats(self):
        if not self.exams: #se non ci sono voti lascia — nei campi delle medie
            self.var_avg.set("—")
            self.var_weighted.set("—")
            return

        # Calcolo la media semplice per avere un colpo d'occhio immediato sui voti
        grades = [exam["grade"] for exam in self.exams]
        avg = sum(grades) / len(grades)

        total_weight = sum(exam["cfu"] for exam in self.exams)
        if total_weight > 0:
            # Media ponderata classica: somma(voto*CFU) / somma(CFU)
            weighted = sum(exam["grade"] * exam["cfu"] for exam in self.exams) / total_weight
            self.var_weighted.set(f"{weighted:.2f}")
        else:
            self.var_weighted.set("—")

        self.var_avg.set(f"{avg:.2f}")

    def _persist_data(self):
        # Scrivo su disco ogni volta per ridurre il rischio di perdere dati
        save_exams(self.exams)

    def _sort_by(self, column: str):
        if not self.exams:
            return

        if not hasattr(self, "_sort_state"): # Stato per alternare ASC/DESC per ogni colonna
            self._sort_state = {}

        current_desc = self._sort_state.get(column, False) # Ultima direzione usata per questa colonna
        reverse = not current_desc # Inverto per alternare

        # Sceglie la chiave di ordinamento in base alla colonna
        if column == "subject":
            key_fn = lambda exam: exam["subject"].lower()
        elif column == "cfu":
            key_fn = lambda exam: exam["cfu"]
        else:
            key_fn = lambda exam: exam["grade"]

        self.exams.sort(key=key_fn, reverse=reverse) # Ordina la lista in memoria
        self._sort_state[column] = reverse # Aggiorna lo stato (True=desc)
        self._refresh_table()  # Ricostruisce la tabella


    def _remove_selected_exam(self):
        selection = self.tree.selection() # Ottiene l’ID della riga selezionata (se c’è)
        if not selection:
            messagebox.showinfo("Seleziona un esame", "Seleziona un esame da rimuovere.")
            return

        item_id = selection[0]
        values = self.tree.item(item_id, "values") # Legge i valori (subject, cfu, grade) dalla riga
        if not values or len(values) < 3:
            messagebox.showwarning("Esame non valido", "Impossibile identificare l'esame selezionato.")
            return

        subject, cfu, grade = values
        # Chiedo conferma
        if not messagebox.askyesno("Conferma rimozione", f"Vuoi eliminare l'esame '{subject}'?"):
            return
        
        for idx, exam in enumerate(self.exams): # Cerca la prima corrispondenza esatta nell’elenco in memoria
            if (
                exam.get("subject") == subject
                and str(exam.get("cfu")) == str(cfu)
                and f"{exam.get('grade'):.1f}" == str(grade)
            ):
                # Trovo la prima corrispondenza esatta e la rimuovo: l'elenco viene ricostruito subito dopo
                self.exams.pop(idx)
                self._persist_data()
                self._refresh_table()
                self._update_stats()
                return

        # Caso limite: l'esame non esiste più (magari è stato riordinato/rimosso altrove)
        messagebox.showwarning("Esame non trovato", "L'esame selezionato non è più disponibile.")

    def _apply_tree_styles(self):
        if not hasattr(self, "tree"):
            return
        palette = getattr(self.winfo_toplevel(), "_planner_palette", None) # Prova a leggere i colori dal tema applicato al root (palette personalizzata)
        if palette is not None:
            even_bg = palette.surface # Colore righe pari
            odd_bg = palette.alternate # Colore righe dispari
            fg = palette.text # Colore testo
        else:
            even_bg = "#FFFFFF"
            odd_bg = "#F1F5F9"
            fg = "#111111"
        self.tree.tag_configure("evenrow", background=even_bg, foreground=fg) # Applica i colori ai tag delle righe
        self.tree.tag_configure("oddrow", background=odd_bg, foreground=fg)

    def _on_theme_change(self, _event=None):
        self._apply_tree_styles()  # Richiamata quando cambia il tema: ri-applica gli stili alla tabella


def create_exams_tab(parent: tk.Widget) -> ttk.Frame: # Funzione factory usata da chi costruisce il Notebook per creare la tab "Esami"
    return ExamsTab(parent)
