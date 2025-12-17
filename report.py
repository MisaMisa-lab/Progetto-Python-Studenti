from datetime import date, datetime


def somma(tempo_studiato, periodo: str = "oggi") -> int:
    oggi = date.today()
    anno_iso, settimana_iso, _ = oggi.isocalendar()
    totale = 0

    def _parse_data(iso_str: str) -> date:
        try:
            return date.fromisoformat(iso_str)
        except ValueError:
            return datetime.strptime(iso_str, "%d-%m-%y").date()

    # Scorro tutte le sessioni e accumulo solo quelle che rientrano nell'intervallo richiesto
    for sessions in tempo_studiato.values():
        for s in sessions:
            d = _parse_data(s["data"])
            minuti = s["minuti"]

            if periodo == "oggi":
                # Confronto diretto con la data corrente
                if d == oggi:
                    totale += minuti
            elif periodo == "settimana":
                anno, settimana, _ = d.isocalendar()
                if anno == anno_iso and settimana == settimana_iso:
                    totale += minuti
            elif periodo == "mese":
                # Qui mi basta verificare mese e anno
                if d.year == oggi.year and d.month == oggi.month:
                    totale += minuti
    return totale


def fmt_mm(minuti: int) -> str:
    # Converto i minuti nel formato "xh ym" per dare un feedback immediato nelle etichette
    return f"{minuti // 60}h {minuti % 60}m"
