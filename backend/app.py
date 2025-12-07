from flask import Flask, request, jsonify
from flask import send_from_directory
import os
from werkzeug.utils import secure_filename
from PIL import Image

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
RESULTS_FOLDER = os.path.join(BASE_DIR, "results")
# /backend/app.py

# ... (path logic) ...
PROJECT_ROOT = os.path.join(BASE_DIR, "..")
# 1. Join the path to 'frontend'
unnormalized_path = os.path.join(PROJECT_ROOT, "frontend")

# 2. FORCE the path to be clean, resolving the '..'
FRONTEND_FOLDER = os.path.normpath(unnormalized_path)

print(f"--- DIAGNOSTIC PATH --- The calculated FRONTEND_FOLDER is: {FRONTEND_FOLDER}")
# ...
ALLOWED_EXT = {"png","jpg","jpeg","pdf"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

# Update Flask to use the absolute path
app = Flask(__name__, static_folder=FRONTEND_FOLDER, static_url_path="/")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# ... rest of your code ...

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
        analysis = full_analyze(file_path)
        return jsonify({"file_id": filename, **analysis}) #jsonify({"status": "ok", "text": text})

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
    # 1. Try to find the specific file (e.g., css/style.css)
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)

    # 2. If file not found, check if index.html exists
    if os.path.exists(os.path.join(app.static_folder, "index.html")):
        return send_from_directory(app.static_folder, "index.html")

    # 3. If index.html is missing, return a text error so we know what's wrong
    return f"Error: index.html not found in {app.static_folder}", 404

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

