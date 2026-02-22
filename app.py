import os
from flask import Flask, render_template, request, jsonify
from groq import Groq

app = Flask(__name__)

# Groq API Key
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in environment variables")

client = Groq(api_key=GROQ_API_KEY)

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
        data = request.get_json()
        user_message = data.get("message") if data else None

        if not user_message:
            return jsonify({"reply": "Baby kuch to bolo 😅"})

        completion = client.chat.completions.create(
            model="openai/gpt-oss-20b",   # ✅ Stable free-friendly model
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            temperature=0.8,
            max_tokens=120
        )

        reply = completion.choices[0].message.content.strip()

        if not reply:
            reply = "Baby mujhe samajh nahi aaya 😅"

        return jsonify({"reply": reply})

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"reply": "Baby thoda network issue aa gaya 😔 try again"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
