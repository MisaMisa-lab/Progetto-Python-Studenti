from datetime import date, datetime
import time #serve per gestire il tempo
import os

from storage import load_data, save_data, FILE_NAME


#GESTIONE INPUT
def input_materia (prompt = "Per quale materia vorresti studiare: ") -> str : #controllo che la materia inserita e valida
    while True :
        materia = input(prompt).strip().lower()
        if materia :
            return materia
        print ("La materia non puo essere vuota")

def input_minuti(prompt: str) -> str : #controllo che il tempo inserito sia valido
    while True :
        raw = input(prompt).strip()
        try :
            val = int (raw)
            if val > 0 :
                return val
            print ("Inserisci un numero intero maggiore di 0")
        except ValueError :
            print ("Inserici un numero intero")


#SALVA
def salva_sessione (tempo_studiato : dict, materia : str, minuti : int, motivo : str = "completata") :
    if minuti <= 0 :
        print ("[INFO] nessun minuto utile da salvare")
        return
    oggi = date.today().isoformat()
    tempo_studiato.setdefault(materia , [])
    tempo_studiato[materia].append({"data": oggi, "minuti": int(minuti)})
    save_data(tempo_studiato, FILE_NAME)
    print (f"[SALVATO] {materia.capitalize()} > {minuti} min > {oggi} > motivo : {motivo} > file : {FILE_NAME}")


#COUNTDOWN
def countdown_studio (minuti_target : int, materia : str, tempo_studiato : dict) :
    sec_target = minuti_target * 60
    start = time.time()

    try :
        print (f"Inizio studio {materia} > target {minuti_target} min")
        sec_restanti = sec_target
        while sec_restanti >= 0 :
            m, s = divmod(sec_restanti, 60)
            print (f"{m:02d}:{s:02d}", end = "\r")
            time.sleep(1)
            sec_restanti-=1
        print ("Sessione studio completata!")
        salva_sessione(tempo_studiato, materia, minuti_target, motivo = "completata")

    except KeyboardInterrupt :
        elapsed_sec = max(0, int(time.time() - start))
        minuti_fatti = elapsed_sec // 60
        print ("\n Interruzione sessione")
        if minuti_fatti > 0 :
            salva_sessione(tempo_studiato, materia, minuti_fatti, motivo = "interrotta")
        else :
            print("Impossibile salvare : meno di 1 minuto svolto")

def countdown_riposo (minuti: int) :
    sec = minuti * 60
    print (f"Inizio pausa di {minuti} min")
    while sec >= 0 :
        m , s = divmod(sec, 60)
        print (f"{m:02d}:{s:02d}", end = "\r")
        time.sleep(1)
        sec-=1
    print ("\n E ora di rimettersi a studiare!")

#MAIN
def main () :
    print ("Pomodoro Timer")
    tempo_studiato = load_data(FILE_NAME)

    materia = input_materia() #faccio inserire all'utente la materia 
    studio = input_minuti("Quanto tempo vorresti studiare? (minuti) ")#faccio inserire all'utente quanto tempo vuole studiare
    riposo = input_minuti("Quanto tempo vorresti riposare? (minuti) ") #faccio inserire all'utente quanto tempo vuole riposare

    continua = True #verifico se l'utente vuole continuare a studiare

    while continua : # fin che l'utente decide di continuare a studiare

        countdown_studio (studio, materia, tempo_studiato)
        countdown_riposo (riposo)
        risposta = input ("Desideri continuare? [s/n] ").strip().lower() #controlla se l'utente vuole continuare a studiare 
        if risposta != "s" :
            nuova = input("Vuoi cambiare matria? [s/n]").strip().lower() #chiede all'utente se vuole iniziare a studiare un altra materia
            if nuova != "s" :
                continua = False
            else :
                materia = input("Per quale materia vorresti studiare: ").strip().lower() #se si chiede l'inserimento nel dizionario di un altra materia
    
    save_data(tempo_studiato, FILE_NAME)

if __name__ == "__main__" :
    main()