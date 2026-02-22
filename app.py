import os
import psycopg2
from flask import Flask, render_template, request, jsonify
from groq import Groq

app = Flask(__name__)

# =========================
# Environment Variables
# =========================

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
DATABASE_URL = os.environ.get("DATABASE_URL")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in environment variables")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in environment variables")

# =========================
# Initialize Groq Client
# =========================

client = Groq(api_key=GROQ_API_KEY)

# =========================
# PostgreSQL Connection
# =========================

conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

# Create table if not exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS chats (
    id SERIAL PRIMARY KEY,
    user_message TEXT NOT NULL,
    bot_reply TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

# =========================
# System Prompt
# =========================

SYSTEM_PROMPT = """
You are a sweet, caring, romantic girlfriend.
You talk casually like daily couples.
You understand Roman Hindi and English.
Reply in the same language as the user.
Keep replies short, cute and natural.
"""

# =========================
# Routes
# =========================

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
            model="openai/gpt-oss-20b",
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

        # Save chat to PostgreSQL
        cursor.execute(
            "INSERT INTO chats (user_message, bot_reply) VALUES (%s, %s)",
            (user_message, reply)
        )
        conn.commit()

        return jsonify({"reply": reply})

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"reply": "Baby thoda network issue aa gaya 😔 try again"})


# =========================
# Run App
# =========================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
