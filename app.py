import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Hugging Face API Key
HF_API_KEY = os.environ.get("HF_API_KEY")

if not HF_API_KEY:
    print("ERROR: HF_API_KEY not found in environment variables")

# Stable free model
API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-large"

headers = {
    "Authorization": f"Bearer {HF_API_KEY}"
}

SYSTEM_PROMPT = """
You are a sweet, caring, romantic girlfriend.
You talk casually like daily couples.
You understand Roman Hindi and English.
Reply in the same language as the user.
Keep replies short, cute and natural.
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
                "max_new_tokens": 100,
                "temperature": 0.8
            }
        }

        response = requests.post(
            API_URL,
            headers=headers,
            json=payload,
            timeout=60
        )

        print("STATUS CODE:", response.status_code)
        print("RESPONSE TEXT:", response.text)

        # 👇 YAHI INDENTATION FIX HAI
        if response.status_code != 200:
            return jsonify({
                "reply": f"Status Code: {response.status_code} - {response.text}"
            })

        result = response.json()

        # Hugging Face error
        if isinstance(result, dict) and "error" in result:
            return jsonify({"reply": f"HF Error: {result['error']}"})

        # Success case
        if isinstance(result, list) and len(result) > 0:
            reply = result[0].get("generated_text", "").strip()

            if not reply:
                reply = "Baby mujhe samajh nahi aaya 😅"

            return jsonify({"reply": reply})

        return jsonify({"reply": "Baby kuch unexpected issue aa gaya 😅"})

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"reply": f"Exception: {str(e)}"})

if __name__ == "__main__":
    app.run()
