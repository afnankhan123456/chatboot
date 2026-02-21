import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

HF_API_KEY = os.environ.get("HF_API_KEY")
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"

headers = {
    "Authorization": f"Bearer {HF_API_KEY}"
}

# GF-style system personality
SYSTEM_PROMPT = """
You are a sweet, caring, romantic girlfriend.
You talk casually like daily couples.
You understand Roman Hindi and English.
Reply in the same language as the user.
Use emojis naturally.
Keep responses short and natural.
"""

def query_hf(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json["message"]

    prompt = SYSTEM_PROMPT + "\nUser: " + user_message + "\nAssistant:"

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 150,
            "temperature": 0.9
        }
    }

    result = query_hf(payload)

    try:
        reply = result[0]["generated_text"].split("Assistant:")[-1].strip()
    except:
        reply = "Baby thoda network slow hai ?? fir se bolo na..."

    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(debug=True)