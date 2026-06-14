from datetime import datetime, timedelta
from typing import Dict, List

from schedule_storage import load_schedule, save_schedule


DAYS = ("Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato")
REPEAT_OPTIONS = ("No", "Ogni settimana", "Ogni mese")

MONTHS = {
    1: "Gennaio",
    2: "Febbraio",
    3: "Marzo",
    4: "Aprile",
    5: "Maggio",
    6: "Giugno",
    7: "Luglio",
    8: "Agosto",
    9: "Settembre",
    10: "Ottobre",
    11: "Novembre",
    12: "Dicembre",
}


def load_schedule_data() -> Dict[str, List[dict]]:
    data = load_schedule()
    return {day: list(data.get(day, [])) for day in DAYS}


def get_current_day_index() -> int:
    today_index = datetime.now().weekday()

    if today_index < len(DAYS):
        return today_index

    return 0


def get_week_start() -> datetime:
    today = datetime.now()
    return today - timedelta(days=today.weekday())


def get_date_for_day(week_start: datetime, day_index: int) -> datetime:
    return week_start + timedelta(days=day_index)


def get_date_text(week_start: datetime, day_index: int) -> str:
    current_date = get_date_for_day(week_start, day_index)
    month = MONTHS[current_date.month]

    return f"{current_date.day} {month} {current_date.year}"


def get_day_entries(schedule: dict, day: str, current_date: datetime) -> list[dict]:
    entries = []

    for item in schedule.get(day, []):
        if is_visible_on_date(item, current_date):
            entries.append(item)

    return entries


def is_visible_on_date(item: dict, current_date: datetime) -> bool:
    repeat = item.get("repeat", "Ogni settimana")
    item_date_text = item.get("date")

    if not item_date_text:
        return True

    try:
        item_date = datetime.strptime(item_date_text, "%Y-%m-%d")
    except ValueError:
        return True

    if repeat == "No":
        return item_date.date() == current_date.date()

    if repeat == "Ogni settimana":
        return True

    if repeat == "Ogni mese":
        return item_date.day == current_date.day

    return True


def add_activity(
    schedule: dict,
    day: str,
    time: str,
    subject: str,
    notes: str,
    repeat: str,
    activity_date: datetime,
) -> None:
    time = time.strip()
    subject = subject.strip()
    notes = notes.strip()

    if repeat not in REPEAT_OPTIONS:
        repeat = "No"

    if not time or not subject:
        raise ValueError("Inserisci almeno orario e attività.")

    try:
        datetime.strptime(time, "%H:%M")
    except ValueError:
        raise ValueError("Usa il formato HH:MM.")

    schedule[day].append(
        {
            "time": time,
            "subject": subject,
            "notes": notes,
            "repeat": repeat,
            "date": activity_date.date().isoformat(),
        }
    )

    schedule[day].sort(key=lambda item: item["time"])
    save_schedule(schedule)


def remove_activity(schedule: dict, day: str, time: str, subject: str, repeat: str, notes: str) -> bool:
    for index, item in enumerate(schedule[day]):
        same_time = item.get("time", "") == time
        same_subject = item.get("subject", "") == subject
        same_repeat = item.get("repeat", "Ogni settimana") == repeat
        same_notes = item.get("notes", "") == notes

        if same_time and same_subject and same_repeat and same_notes:
            schedule[day].pop(index)
            save_schedule(schedule)
            return True

    return False


def sort_activities(schedule: dict, day: str, column: str, reverse: bool = False) -> None:
    def key(item):
        value = item.get(column, "")

        if isinstance(value, str):
            return value.lower()

        return value

    schedule[day].sort(key=key, reverse=reverse)
    save_schedule(schedule)