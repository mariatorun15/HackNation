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
    m = re.search(r"(\d{2}[.\-/]\d{2}[.\-/]\d{4})", text)
    if m:
        return m.group(1)
    m = re.search(r"(\d{4}[.\-/]\d{2}[.\-/]\d{2})", text)
    if m:
        return m.group(1)
    
    return None

def find_time(text):
    if not text:
        return None
    # dd.mm.yyyy or yyyy-mm-dd etc.
    m = re.search(r'godz\. *(około *)?(\d{1,2}(:\d{2})?)', text)
    if m:
        return m.group(2)
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
    

def find_name(text):
    # naive: line with CAPITALIZED words (Polish names)
    if not text:
        return None
    lines = text.splitlines()
    for line in lines:
        if re.match(r"^[A-ZĄĆĘŁŃÓŚŹŻ][a-ząęćłńóśźż]+(\s+[A-ZĄĆĘŁŃÓŚŹŻ][a-ząęćłńóśźż]+)+", line.strip()):
            return line.strip()
    return None

def find_vehicle_number(text):
    if not text:
        return None
    m = re.search(r"\b([A-Z]{1,3}-\w{1,5})\b", text)
    if m:
        return m.group(1)
    return None
