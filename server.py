from flask import Flask, request, jsonify
from google import genai
import os
import traceback

app = Flask(__name__)

# --------------------------------------------------
# Configuration
# --------------------------------------------------

API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    print("STARTUP ERROR: GEMINI_API_KEY is not set", flush=True)
else:
    print("STARTUP: GEMINI_API_KEY is available", flush=True)

client = genai.Client(api_key=API_KEY)

MODEL = "gemini-2.5-flash"


# --------------------------------------------------
# Basic routes
# --------------------------------------------------

@app.route("/", methods=["GET"])
def home():
    return "JARVIS backend is online."


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "service": "jarvis-backend"
    })


# --------------------------------------------------
# Gemini chat route
# --------------------------------------------------

@app.route("/chat", methods=["POST"])
def chat():

    print("CHAT: request received", flush=True)

    try:
        # Read JSON sent by the Android app
        data = request.get_json(silent=True)

        print("CHAT: JSON received:", data, flush=True)

        if not data:
            print("CHAT ERROR: no JSON body", flush=True)

            return jsonify({
                "error": "Request body must contain JSON."
            }), 400

        # Get user's message
        user_message = data.get("message")

        if not isinstance(user_message, str):
            print("CHAT ERROR: message is missing or not text", flush=True)

            return jsonify({
                "error": "The 'message' field must be text."
            }), 400

        user_message = user_message.strip()

        print(
            "CHAT: message length:",
            len(user_message),
            flush=True
        )

        if not user_message:
            print("CHAT ERROR: empty message", flush=True)

            return jsonify({
                "error": "Message cannot be empty."
            }), 400

        # Make sure API key exists
        if not API_KEY:
            print(
                "GEMINI ERROR: GEMINI_API_KEY is missing",
                flush=True
            )

            return jsonify({
                "error": "Gemini API key is not configured."
            }), 500

        # Send request to Gemini
        print(
            "CHAT: sending request to Gemini...",
            flush=True
        )

        response = client.models.generate_content(
            model=MODEL,
            contents=user_message
        )

        print(
            "CHAT: Gemini response received",
            flush=True
        )

        # Extract response text safely
        reply = response.text

        if not reply:
            print(
                "GEMINI ERROR: Gemini returned empty text",
                flush=True
            )

            return jsonify({
                "error": "Gemini returned an empty response."
            }), 500

        print(
            "CHAT: reply generated successfully",
            flush=True
        )

        return jsonify({
            "reply": reply
        }), 200

    except Exception as e:

        print(
            "GEMINI ERROR:",
            repr(e),
            flush=True
        )

        print(
            "FULL TRACEBACK:",
            flush=True
        )

        traceback.print_exc()

        return jsonify({
            "error": "Gemini request failed."
        }), 500


# --------------------------------------------------
# Start server
# --------------------------------------------------

if __name__ == "__main__":

    port = int(
        os.environ.get("PORT", 10000)
    )

    print(
        f"STARTING JARVIS BACKEND ON PORT {port}",
        flush=True
    )

    app.run(
        host="0.0.0.0",
        port=port
    )
