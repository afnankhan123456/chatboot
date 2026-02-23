import os
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise RuntimeError("GOOGLE_API_KEY missing")

# Initialize Google model
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

@app.route("/")
def home():
    return "GOOGLE SERVER WORKING"

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message")

        response = model.generate_content(
            user_message,
            generation_config={
                "temperature": 0.7,
                "max_output_tokens": 100,
            }
        )

        return jsonify({"reply": response.text})

    except Exception as e:
        print("Google error:", e)
        return jsonify({"reply": "Google error"})
