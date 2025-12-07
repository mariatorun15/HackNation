# backend/app.py
from flask import Flask, request, jsonify
from flask import send_from_directory
import os
from werkzeug.utils import secure_filename
from PIL import Image
import pytesseract
from utils import allowed_file, analyze_file, extract_text, full_analyze

UPLOAD_FOLDER = "uploads"
RESULTS_FOLDER = "results"
ALLOWED_EXT = {"png","jpg","jpeg","pdf"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

app = Flask(__name__, static_folder="../frontend", static_url_path="/")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# --- ENDPOINT ---

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "Brak pliku"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Plik nie ma nazwy"}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(file_path)
        #text = extract_text(file_path)
        #analysis = full_analyze(file_path)
        #return jsonify({"file_id": filename, **analysis}) #jsonify({"status": "ok", "text": text})
 
        analysis = full_analyze(file_path)

        # --- Zapis analizy do pliku JSON ---
        import json
        out_path = os.path.join(RESULTS_FOLDER, filename + "_analysis.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump({"file_id": filename, **analysis}, f, ensure_ascii=False, indent=2)
        # --- KONIEC ZAPISU ---

        return jsonify({"file_id": filename, **analysis, "path": out_path})

    return jsonify({"error": "Nieobsługiwany format"}), 400

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json() or {}
    question = data.get("question", "").strip()
    context = data["context"]

    if not question:
        return jsonify({"answer": "Proszę zadać pytanie."}), 400
    
    #response = call_llm(question, context)

    # PROSTA LOGIKA: zamieniemy to później na AI/LLM
    if "dzień" in question.lower() or "dzień dobry" in question.lower():
        answer = "Dzień dobry! Jak mogę pomóc?"
    elif "składki" in question.lower():
        answer = "Termin opłacania składek to zwykle do 10/15/20 dnia miesiąca — sprawdź swój przypadek."
    else:
        answer = "Niestety nie znam odpowiedzi — skontaktuj się z obsługą."

    return jsonify({"answer": answer})


@app.route("/compare", methods=["POST"])
def compare():
    import json

    data = request.get_json() or {}
    files = data.get("files", [])

    if not files:
        return jsonify({"error": "Brak listy plików"}), 400

    loaded = []
    for f in files:
        path = os.path.join(RESULTS_FOLDER, f)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as fp:
                loaded.append(json.load(fp))

    if not loaded:
        return jsonify({"error": "Brak poprawnych plików"}), 400

    # -------------------------
    # PORÓWNANIE PARAMETRÓW
    # -------------------------
    diffs = {}
    matches = {}

    all_keys = set()
    for doc in loaded:
        # używamy filled_fields jeśli istnieje, inaczej extracted
        fields = doc.get("filled_fields") or doc.get("extracted") or {}
        all_keys |= set(fields.keys())

    for key in all_keys:
        values = [ (doc.get("filled_fields") or doc.get("extracted") or {}).get(key) for doc in loaded]
        unique_values = set([v for v in values if v is not None])
        if len(unique_values) == 0:
            continue
        elif len(unique_values) == 1:
            matches[key] = list(unique_values)[0]
        else:
            diffs[key] = list(unique_values)

    # -------------------------
    # ROZSZERZONY WNIOSEK
    # -------------------------
    consistency_report = []
    strong_signals = 0
    weak_signals = 0

    for key in all_keys:
        values = [ (doc.get("filled_fields") or doc.get("extracted") or {}).get(key) for doc in loaded]
        non_null = [v for v in values if v is not None]
        if not non_null:
            continue
        unique_values = set(non_null)
        most_common_value = max(set(non_null), key=non_null.count)
        ratio = non_null.count(most_common_value) / len(non_null)

        label = key.replace("_", " ").capitalize()

        if len(unique_values) == 1:
            consistency_report.append(f"✔ {label}: wszystkie dokumenty są zgodne ({most_common_value}).")
            strong_signals += 1
        elif ratio > 0.6:
            consistency_report.append(f"≈ {label}: większość dokumentów podaje {most_common_value}, ale występują też inne wartości: {list(unique_values)}.")
            weak_signals += 1
        else:
            consistency_report.append(f"✘ {label}: wartości różnią się znacząco ({list(unique_values)}).")

    if strong_signals >= 3:
        final_conclusion = "Dokumenty wykazują wysoki poziom spójności – zdarzenie jest prawdopodobne."
    elif strong_signals >= 1 or weak_signals >= 2:
        final_conclusion = "Dokumenty są częściowo zgodne – zdarzenie umiarkowanie prawdopodobne."
    else:
        final_conclusion = "Dokumenty są niespójne – nie można potwierdzić zdarzenia."

    return jsonify({
        "różnice": diffs,
        "zgodności": matches,
        "wniosek_szczegółowy": consistency_report,
        "wniosek_końcowy": final_conclusion
    })


@app.route("/results", methods=["GET"])
def list_results():
    files = [f for f in os.listdir(RESULTS_FOLDER) if f.endswith("_analysis.json")]
    return jsonify(files)


@app.route("/complete", methods=["POST"])
def complete():
    data = request.json or {}
    file_id = data.get("file_id")
    filled = data.get("filled_fields") or {}
    if not file_id:
        return jsonify({"error":"Brak file_id"}), 400
    # zapisz wynik końcowy do results/file_id.json
    out = {
        "file_id": file_id,
        "filled_fields": filled
    }
    out_path = os.path.join(RESULTS_FOLDER, file_id + ".json")
    import json
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    return jsonify({"status":"saved", "path": out_path})

# opcjonalnie serwowanie frontendu statycznego (przy hostingu jednego serwera)
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_frontend(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, "panel.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    file_id = data.get("file_id")
    if not file_id:
        return jsonify({"error": "Brak file_id"}), 400

    file_path = os.path.join(app.config["UPLOAD_FOLDER"], file_id)
    if not os.path.exists(file_path):
        return jsonify({"error": "Plik nie istnieje"}), 404

    result = analyze_file(file_path)
    return jsonify(result)

# --- URUCHOMIENIE SERWERA ---

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)

