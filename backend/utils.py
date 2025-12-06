from pypdf import PdfReader
import pytesseract
from PIL import Image
import docx

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

