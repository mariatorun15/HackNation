# backend/app.py

from flask import Flask, request, jsonify
from flask import send_from_directory
import os
from werkzeug.utils import secure_filename
from PIL import Image
import pytesseract
from utils import allowed_file, analyze_file, extract_text

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"png", "pdf"}

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
        text = extract_text(file_path)
        return jsonify({"status": "ok", "text": text})

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

# opcjonalnie serwowanie frontendu statycznego (przy hostingu jednego serwera)
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_frontend(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, "index.html")

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

