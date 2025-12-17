import json
import os
import sys
from typing import List, Dict, Any

FILE_NAME = "exams.json"


def load_exams(file_name: str = FILE_NAME) -> List[Dict[str, Any]]:
    if not os.path.exists(file_name):
        return []
    try:
        with open(file_name, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        if isinstance(data, list):
            return data
    except Exception as exc: 
        print(f"[ATTENZIONE] impossibile leggere {file_name}: {exc}", file=sys.stderr)
    return []


def save_exams(data: List[Dict[str, Any]], file_name: str = FILE_NAME) -> None:
    try:
        tmp_name = file_name + ".tmp"
        with open(tmp_name, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=4)
        os.replace(tmp_name, file_name)
    except Exception as exc:  
        print(f"[ERRORE] salvataggio file fallito ({file_name}): {exc}", file=sys.stderr)
