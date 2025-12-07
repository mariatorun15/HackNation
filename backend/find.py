import re

def extract_option(pattern, text):
    """Funkcja wyciąga odpowiedź TAK/NIE, jeśli brak to zwraca 'nie wiem'"""
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        # Wyszukujemy pierwszą z możliwych opcji: TAK/NIE/TBD
        if "tak" in match.group(1).lower():
            return "TAK"
        elif "nie" in match.group(1).lower():
            return "NIE"
    return "NIE WIEM"

def find_date(text):
    if not text:
        return None
    # dd.mm.yyyy or yyyy-mm-dd etc.
    m = re.search(r"(\d{2}[.\-/—]\d{2}[.\-/—]\d{4})", text)
    if m:
        return m.group(1)
    m = re.search(r"(\d{4}[.\-/—]\d{2}[.\-/—]\d{2})", text)
    if m:
        return m.group(1)
    
    return None

def find_sit_time(text):
    if not text:
        return None
    m = re.search(r'około\s*godz\.?\s*[: ]?(\d{1,2}[.:]\d{2})', text, re.IGNORECASE)
    if m:
        return m.group(1)
    return None

def find_start_time(text):
    if not text:
        return None
    m = re.search(r'rozpoczął.*?o\s*godz\.?\s*(\d{1,2}[.:]\d{2})', text, re.IGNORECASE)
    if m:
        return m.group(1)
    return None

def find_end_time(text):
    if not text:
        return None
    m = re.search(
        r'(?:planowana\s+)?godzina\s+zakończenia\s+pracy\s*(\d{1,2}[.:]\d{2})',
        text,
        re.IGNORECASE
    )
    if m:
        return m.group(1)
    return None


def find_place(text):
    if not text:
        return None
    # dd.mm.yyyy or yyyy-mm-dd etc.
    m = re.search(r'miejsce.*?([\w\s]+?)(\.|\n)', text)
    if m:
        return m.group(1)
    else:
        m = re.search(r'\d{2}\.\d{2}\.\d{4}r?\.*\s*[,\.]*\s*(.*?)\.*godz', text)
        return m.group(1)
    return None

def find_injuries(text):
    if not text:
        return None
    # dd.mm.yyyy or yyyy-mm-dd etc.
    m = re.search(r'Rodzaj doznanych urazów\s*(.*?)\n', text, re.DOTALL)
    if m:
        return m.group(1).strip()
    m = re.search(r'rozpoznano: (.*?)(?:\.|,)', text)
    if m:
        return m.group(1).strip()
    return None

def find_history(text):
    if not text:
        return None
    # dd.mm.yyyy or yyyy-mm-dd etc.
    m = re.search(r'Szczegółowy opis.*?wypadku\s*(.*?)\n6\.', text, re.DOTALL)
    if m:
        return m.group(1).strip()
    return None

def find_aid(text):
    if not text:
        return None
    # dd.mm.yyyy or yyyy-mm-dd etc.
    m = extract_option(r'Czy była udzielona pierwsza pomoc medyczna:\s*(TAK|NIE)', text)
    if m:
        return m
    m = re.search(r'Pierwszej pomocy udzielono (.*?)(?:\.|,)', text)
    if m:
        return m.group(1).strip()
    return None

def find_mashine(text):
    if not text:
        return None
    # dd.mm.yyyy or yyyy-mm-dd etc.
    m = extract_option(r'Czy wypadek powstał podczas obsługi maszyn, urządzeń.*?(\bTAK\b|\bNIE\b)', text)
    if m:
        return m
    return None

def find_bhp(text):
    if not text:
        return None
    # dd.mm.yyyy or yyyy-mm-dd etc.
    m = extract_option(r'W trakcie pracy przestrzegałem/am zasad BHP.*?:\s*(.*)', text)
    if m:
        return m
    return None
    
