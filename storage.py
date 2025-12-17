import json # serve per caricare il file con i dati
import os #serve per controllare se esiste il file
import sys 

FILE_NAME = "studio.json"

def load_data(file_name: str = FILE_NAME) -> dict :
    if not os.path.exists(file_name) :
        return {}
    try : #controllo
        with open (file_name, "r", encoding = "utf-8") as f: #lo apro in modalita lettura
            data = json.load(f) #leggo 
        return data if isinstance(data, dict) else{}
    except Exception as e :
        print (f"[ATTENZIONE] imposibile leggere {file_name}: {e}", file = sys.stderr)
        return {}

def save_data(data: dict, file_name: str = FILE_NAME) -> None : 
    #salvataggio creato per salvare ogni volta e non solo alla fine di tutto (fa prima un file temporaneo)
    try :
        tmp = file_name + ".tmp"
        with open(tmp, "w", encoding = "utf-8") as f :
            json.dump(data, f, indent = 4, ensure_ascii=False) #scrivo nel file
        os.replace(tmp, file_name)
    except Exception as e :
        print (f"[ERRORE] salvataggio file  fallito ({file_name}): {e}", file = sys.stderr)
        