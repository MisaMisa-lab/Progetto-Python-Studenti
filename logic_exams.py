from typing import Dict, List

from exam_storage import load_exams, save_exams


def load_exams_data() -> List[Dict[str, float]]:
    return load_exams()


def format_grade(grade: float) -> str:
    grade = float(grade)

    if grade.is_integer():
        return str(int(grade))

    return f"{grade:.1f}"


def add_exam(exams: list, subject: str, cfu_text: str, grade_text: str) -> None:
    subject = subject.strip()
    cfu_text = cfu_text.strip()
    grade_text = grade_text.strip()

    if not subject or not cfu_text or not grade_text:
        raise ValueError("Compila materia, CFU e voto.")

    try:
        cfu = int(cfu_text)
        if cfu <= 0:
            raise ValueError
    except ValueError:
        raise ValueError("Inserisci un numero intero positivo per i CFU.")

    try:
        grade = float(grade_text.replace(",", "."))
    except ValueError:
        raise ValueError("Inserisci un voto valido.")

    if not 0 <= grade <= 30:
        raise ValueError("Il voto deve essere tra 0 e 30.")

    exams.append(
        {
            "subject": subject,
            "cfu": cfu,
            "grade": grade,
        }
    )

    save_exams(exams)


def remove_exam(exams: list, subject: str, cfu: str, grade: str) -> bool:
    for index, exam in enumerate(exams):
        same_subject = exam["subject"] == subject
        same_cfu = str(exam["cfu"]) == str(cfu)
        same_grade = format_grade(exam["grade"]) == str(grade)

        if same_subject and same_cfu and same_grade:
            exams.pop(index)
            save_exams(exams)
            return True

    return False


def sort_exams(exams: list, column: str, reverse: bool = False) -> None:
    if column == "subject":
        key = lambda exam: exam["subject"].lower()
    else:
        key = lambda exam: exam[column]

    exams.sort(key=key, reverse=reverse)
    save_exams(exams)


def calculate_averages(exams: list) -> tuple[str, str]:
    if not exams:
        return "—", "—"

    grades = [exam["grade"] for exam in exams]
    average = sum(grades) / len(grades)

    total_cfu = sum(exam["cfu"] for exam in exams)

    if total_cfu == 0:
        return format_number(average), "—"

    weighted = sum(exam["grade"] * exam["cfu"] for exam in exams) / total_cfu

    return format_number(average), format_number(weighted)


def format_number(value: float) -> str:
    return f"{value:.2f}".replace(".", ",")