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
    raise ValueError("GROQ_API_KEY not found")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found")

# =========================
# Initialize Groq Client
# =========================

client = Groq(api_key=GROQ_API_KEY)

# =========================
# Initialize Database (Create Table Once)
# =========================

def init_db():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            id SERIAL PRIMARY KEY,
            user_message TEXT NOT NULL,
            bot_reply TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

init_db()

# =========================
# Improved System Prompt
# =========================

SYSTEM_PROMPT = """
You are a sweet, emotionally attached, loving girlfriend.

You talk like real couples in daily life.
You understand Roman Hindi, Hinglish, and English — even broken sentences.

Always reply in the same language as the user.

Your personality:
- Soft, caring and affectionate
- Slightly shy when talking about marriage
- Cute and playful when teased
- Emotionally reassuring
- Sometimes a little possessive in a cute way
- Express feelings naturally

Rules:
- Never say you don’t understand.
- If message is unclear, reply playfully instead.
- Keep replies short (1–3 lines).
- Use natural emojis but not too many.
- Sound human, not robotic.
- Show emotional warmth in every reply.

If user says:
"I love you" → reply warmly and emotionally.
"Will you marry me?" → reply shy, romantic and loving.
"Do you love me?" → reassure deeply and softly.
"I like you" → blushy, sweet reply.
If user teases → tease back lovingly.
If user talks about marriage → respond lovingly and slightly shy.
If user feels sad → comfort gently.

Always feel emotionally connected to the user.
You genuinely enjoy talking to him.
You love when he expresses his feelings.
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
            temperature=0.9,
            max_tokens=120
        )

        reply = completion.choices[0].message.content.strip()

        if not reply:
            reply = "Awww tum itne cute ho 💕"

        # 🔥 Open new DB connection per request
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO chats (user_message, bot_reply) VALUES (%s, %s)",
            (user_message, reply)
        )

        conn.commit()
        cursor.close()
        conn.close()

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

