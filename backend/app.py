# backend/app.py
from flask import Flask, request, jsonify
from flask import send_from_directory
import os

app = Flask(__name__, static_folder="../frontend", static_url_path="/")

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json() or {}
    question = data.get("question", "").strip()
    if not question:
        return jsonify({"answer": "Proszę zadać pytanie."}), 400

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
