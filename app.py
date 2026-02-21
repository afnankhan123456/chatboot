import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Hugging Face API Key
HF_API_KEY = os.environ.get("HF_API_KEY")

API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"

headers = {
    "Authorization": f"Bearer {HF_API_KEY}"
}

# GF-style personality
SYSTEM_PROMPT = """
You are a sweet, caring, romantic girlfriend.
You talk casually like daily couples.
You understand Roman Hindi and English.
Reply in the same language as the user.
Use emojis naturally.
Keep responses short and natural.
"""

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        user_message = request.json.get("message")

        if not user_message:
            return jsonify({"reply": "Baby kuch to bolo 😅"})

        prompt = f"{SYSTEM_PROMPT}\nUser: {user_message}\nAssistant:"

        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 150,
                "temperature": 0.9,
                "return_full_text": False
            }
        }

        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)

        # Agar API fail ho jaye
        if response.status_code != 200:
            return jsonify({"reply": "Baby server thoda busy hai 😅 thodi der baad try karo..."})

        result = response.json()

        # Agar HF error bheje
        if isinstance(result, dict) and "error" in result:
            return jsonify({"reply": "Baby model load ho raha hai 😅 20 second baad try karo..."})

        # Normal success case
        if isinstance(result, list) and len(result) > 0:
            reply = result[0].get("generated_text", "").strip()

            if not reply:
                reply = "Baby mujhe samajh nahi aaya 😅 fir se bolo na..."

            return jsonify({"reply": reply})

        return jsonify({"reply": "Baby kuch technical issue aa gaya 😅"})

    except Exception as e:
        print("Error:", e)
        return jsonify({"reply": "Baby system thoda confuse ho gaya 😅 fir se try karo..."})

if __name__ == "__main__":
    app.run()
