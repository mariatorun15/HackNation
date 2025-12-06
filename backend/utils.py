import os
import re
import json
from PIL import Image
from pdf2image import convert_from_path
import pytesseract
from pypdf import PdfReader
import docx

ALLOWED_EXTENSIONS = {"png", "pdf"}
SCHEMAS_DIR = os.path.join(os.path.dirname(__file__), "schemas")

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def analyze_file(file_path):
    try:
        text = pytesseract.image_to_string(Image.open(file_path), lang="pol")  # lub 'eng'
        # Możesz później wyciągać kwoty, daty itp.
        result = {
            "raw_text": text,
            "extracted": {
                "example_field": "przykład"
            }
        }
        return result
    except Exception as e:
        return {"error": str(e)}
    
# ----------------------------------------------------
"""
def extract_text(file_path):
    if file_path.endswith(".pdf"):
        reader = PdfReader(file_path)
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    if file_path.endswith(".png") or file_path.endswith(".jpg"):
        img = Image.open(file_path)
        return pytesseract.image_to_string(img)

    if file_path.endswith(".docx"):
        doc = docx.Document(file_path)
        return "\n".join(p.text for p in doc.paragraphs)

    return "Unsupported file type"
"""

def extract_data(file_path):
    # Wstępna ekstrakcja danych z OCR / PDF / DOCX
    text = extract_text(file_path)  # funkcja OCR / PDF / DOCX
    data = {
        "numer_dokumentu": find_regex_number(text),
        "kwota": find_regex_amount(text),
        "data": find_regex_date(text)
    }
    return data


def validate_document(data):
    missing = []
    if not data.get("numer_dokumentu"):
        missing.append("numer dokumentu")
    if not data.get("kwota"):
        missing.append("kwota")
    if not data.get("data"):
        missing.append("data")

    if missing:
        return {"status": "wymaga_uzupełnienia", "missing": missing}
    return {"status": "ok"}

# ---- helpers: load schema ----
def load_schema_by_name(name):
    path = os.path.join(SCHEMAS_DIR, f"{name}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_all_schemas():
    schemas = {}
    for fname in os.listdir(SCHEMAS_DIR):
        if fname.endswith(".json"):
            with open(os.path.join(SCHEMAS_DIR, fname), "r", encoding="utf-8") as f:
                s = json.load(f)
                schemas[s["name"]] = s
    return schemas
"""
# ---- extract text from file ----
def extract_text(file_path):
    ext = file_path.rsplit(".", 1)[-1].lower()
    if ext in ("png", "jpg", "jpeg"):
        return pytesseract.image_to_string(Image.open(file_path), lang="pol")
    if ext == "pdf":
        try:
            reader = PdfReader(file_path)
            pages = []
            for p in reader.pages:
                txt = p.extract_text()
                if txt:
                    pages.append(txt)
            combined = "\n".join(pages).strip()
            if combined:
                return combined
            # fallback: render first page to image + OCR if no text extracted
            return ""  # keep simple; can extend with pdf2image
        except Exception as e:
            return ""
    if ext in ("docx",):
        doc = Document(file_path)
        return "\n".join([p.text for p in doc.paragraphs])
    return ""
"""
def extract_text(file_path):
    ext = file_path.rsplit(".", 1)[-1].lower()

    # ---- IMAGES ----
    if ext in ("png", "jpg", "jpeg"):
        return pytesseract.image_to_string(Image.open(file_path), lang="pol")

    # ---- DOCX ----
    if ext == "docx":
        doc = Document(file_path)
        return "\n".join([p.text for p in doc.paragraphs])

    # ---- PDF ----
    if ext == "pdf":
        try:
            # first try direct text extraction
            from pypdf import PdfReader
            reader = PdfReader(file_path)
            text_blocks = []
            for page in reader.pages:
                t = page.extract_text()
                if t:
                    text_blocks.append(t)

            text = "\n".join(text_blocks).strip()

            print(">>> Extracted text preview:")
            print(f">>> File Path: {file_path}")
            print(text[:500])

            # if PDF has embedded text, return it
            if text and len(text) > 20:
                return text
            
            # otherwise: PDF is scanned -> convert to images -> OCR
            images = convert_from_path(file_path, dpi=300, poppler_path=r"C:\poppler-25.12.0\Library\bin")
            ocr_text = ""
            print("PDF pages:", len(images))
            for img in images:
                ocr_text += pytesseract.image_to_string(img, lang="pol")
            
                print(">>> OCR text preview:")
                print(ocr_text[:500])

            return ocr_text

        except Exception as e:
            return ""

    return ""

# ---- detect document type by keywords (simple heuristics) ----
DOCUMENT_KEYWORDS = {
    "karta_wypadku": ["karta wypadku", "rodzaj obrażeń", "miejsce wypadku", "data wypadku"],
    "opinia": ["opinia", "z opinii", "autor opinii", "wskazania"],
    "zapis_wyjasnien_poszkodowanego": ["wyjaśnien", "wyjaśnień", "poszkodowanego", "oświadczam że"],
    "zawiadomienie_o_wypadku": ["zawiadomienie", "zawiadamia", "zawiadomienie o wypadku", "zawiadamiam"]
}

def detect_document_type(text):
    t = (text or "").lower()
    scores = {}
    for doc_type, keys in DOCUMENT_KEYWORDS.items():
        score = sum(1 for k in keys if k in t)
        scores[doc_type] = score
    # pick best with score>0
    best = max(scores.items(), key=lambda x: x[1])
    if best[1] == 0:
        return None
    return best[0]

# ---- simple field extraction heuristics ----
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

def extract_fields_by_type(text, doc_type):
    # return dict with field->value or None
    data = {}
    t = text or ""
    if doc_type == "karta_wypadku":
        data["data_wypadku"] = find_date(t)
        data["miejsce_wypadku"] = None
        data["imie_nazwisko_poszkodowanego"] = find_name(t)
        data["opis_okolicznosci"] = None
        data["rodzaj_obrazen"] = None
        data["numer_pojazdu"] = find_vehicle_number(t)
    elif doc_type == "opinia":
        data["data_opinii"] = find_date(t)
        data["autor_opinii"] = find_name(t)
        data["tresc_opinii"] = None
        data["podpis_autora"] = None
    elif doc_type == "zapis_wyjasnien_poszkodowanego":
        data["data_zapisu"] = find_date(t)
        data["imie_nazwisko_poszkodowanego"] = find_name(t)
        data["opis_zdarzenia"] = None
        data["podpis_poszkodowanego"] = None
    elif doc_type == "zawiadomienie_o_wypadku":
        data["data_zawiadomienia"] = find_date(t)
        data["miejscowosc"] = None
        data["nazwa_pracodawcy"] = None
        data["opis_zdarzenia"] = None
        data["osoby_zaangazowane"] = None
    else:
        data = {}
    return data

# ---- validate against schema ----
def validate_against_schema(extracted, schema):
    missing = []
    for field in schema.get("required_fields", []):
        val = extracted.get(field)
        if val is None or (isinstance(val, str) and val.strip() == ""):
            missing.append(field)
    status = "ok" if not missing else "wymaga_uzupełnienia"
    return {"status": status, "missing": missing, "extracted": extracted}

# ---- convenience: full analyze flow ----
def full_analyze(file_path):
    text = extract_text(file_path)
    doc_type = detect_document_type(text)
    schemas = load_all_schemas()
    schema = schemas.get(doc_type) if doc_type else None
    if not schema:
        # fallback: try to detect by name via filename or default to None
        doc_type = None
        schema = None
    extracted = extract_fields_by_type(text, doc_type) if doc_type else {}
    # fill extracted with values found in text (if heuristics found None, keep None)
    result = validate_against_schema(extracted, schema) if schema else {"status":"unknown","missing":[], "extracted": extracted}
    return {"document_type": doc_type, "raw_text_preview": (text[:1000] if text else ""), **result}