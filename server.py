from flask import Flask, request, jsonify
from google import genai
import os

app = Flask(__name__)

# Gemini client — the API key will be stored securely in Render,
# NOT in this GitHub file.
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

MODEL = "gemini-2.5-flash"


@app.route("/", methods=["GET"])
def home():
    return "JARVIS backend is online."


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=user_message
        )

        return jsonify({
            "reply": response.text
        })

    except Exception as e:
        return jsonify({
            "error": "Gemini request failed",
            "details": str(e)
        }), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
