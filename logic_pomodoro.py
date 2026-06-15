from datetime import date
from typing import Dict, List, Any

from report import fmt_mm, somma

# Importo due funzioni dal file report.py:
# - fmt_mm: trasforma i minuti in un formato leggibile, tipo "1h 30m" oppure simile
# - somma: calcola quanti minuti sono stati studiati in un certo periodo

from storage import FILE_NAME, load_data, save_data
# Importo dal file storage.py:
# - FILE_NAME: nome del file JSON dove salvo i dati del Pomodoro
# - load_data: carica i dati dal JSON
# - save_data: salva i dati nel JSON

def format_seconds(seconds: int) -> str:
    # Converte un numero di secondi in formato MM:SS
    seconds = max(0, int(seconds))
    # Mi assicuro che seconds sia un intero e che non sia mai negativo
    minutes, seconds = divmod(seconds, 60)
    # divmod divide i secondi in minuti e secondi rimanenti
    return f"{minutes:02d}:{seconds:02d}"
    # Restituisco il testo con due cifre per i minuti e due per i secondi


def load_pomodoro_data() -> Dict[str, List[Dict[str, Any]]]:
    return load_data(FILE_NAME)


def save_study_session(data: dict, subject: str, minutes: int) -> bool:
    subject = subject.strip().lower()
    minutes = int(minutes)

    if not subject or minutes <= 0:
        return False

    today = date.today().isoformat()

    data.setdefault(subject, [])
    # Se la materia non esiste ancora nel dizionario, creo una lista vuota.
    data[subject].append(
        {
            "data": today,
            "minuti": minutes,
        }
    )

    save_data(data, FILE_NAME)
    return True


def get_period_stats(data: dict) -> tuple[str, str, str]:
    today = fmt_mm(somma(data, "oggi"))
    week = fmt_mm(somma(data, "settimana"))
    month = fmt_mm(somma(data, "mese"))

    return today, week, month


def get_subject_rows(data: dict) -> list[dict]:
    rows = []

    for subject, sessions in data.items():
        subject_data = {subject: sessions}
        # Creo un mini-dizionario solo con questa materia,

        try:
            today = somma(subject_data, "oggi")
            week = somma(subject_data, "settimana")
            month = somma(subject_data, "mese")
        except Exception:
            today = 0
            week = 0
            month = 0

        total = sum(int(item.get("minuti", 0)) for item in sessions)

        rows.append(
            {
                "materia": subject,
                "oggi": today,
                "settimana": week,
                "mese": month,
                "totale": total,
            }
        )

    return rows


def sort_subject_rows(rows: list[dict], column: str, reverse: bool = False) -> list[dict]:
    # Ordina le righe della tabella in base alla colonna cliccata.
    # reverse=False significa ordine crescente.
    # reverse=True significa ordine decrescente.
    if column == "materia":
        key = lambda row: row["materia"].lower()
    else:
        key = lambda row: row[column]

    return sorted(rows, key=key, reverse=reverse)


def format_minutes(minutes: int) -> str:
    return fmt_mm(minutes)