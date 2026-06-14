from datetime import date
from typing import Dict, List, Any

from report import fmt_mm, somma
from storage import FILE_NAME, load_data, save_data


def format_seconds(seconds: int) -> str:
    seconds = max(0, int(seconds))
    minutes, seconds = divmod(seconds, 60)
    return f"{minutes:02d}:{seconds:02d}"


def load_pomodoro_data() -> Dict[str, List[Dict[str, Any]]]:
    return load_data(FILE_NAME)


def save_study_session(data: dict, subject: str, minutes: int) -> bool:
    subject = subject.strip().lower()
    minutes = int(minutes)

    if not subject or minutes <= 0:
        return False

    today = date.today().isoformat()

    data.setdefault(subject, [])
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
    if column == "materia":
        key = lambda row: row["materia"].lower()
    else:
        key = lambda row: row[column]

    return sorted(rows, key=key, reverse=reverse)


def format_minutes(minutes: int) -> str:
    return fmt_mm(minutes)