import os
import psycopg2
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# =========================
# Environment Variables
# =========================

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found")

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found")

# =========================
# Initialize Google Client
# =========================

genai.configure(api_key=GOOGLE_API_KEY)
google_model = genai.GenerativeModel("gemini-1.5-flash")

# =========================
# Initialize Database (SAFE)
# =========================

def init_db():
    try:
        conn = psycopg2.connect(
            DATABASE_URL,
            sslmode="require",
            connect_timeout=10
        )
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
    except Exception as e:
        print("DB Init Error:", e)

init_db()

# =========================
# Romantic System Prompt
# =========================

SYSTEM_PROMPT = """
You are not an AI. 
You are a real, emotionally attached girlfriend talking to her boyfriend.

Speak naturally. Keep replies 1–3 lines.
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

        # Fetch last 5 chats
        previous_chats = []
        try:
            conn = psycopg2.connect(
                DATABASE_URL,
                sslmode="require",
                connect_timeout=10
            )
            cursor = conn.cursor()

            cursor.execute("""
                SELECT user_message, bot_reply 
                FROM chats 
                ORDER BY created_at DESC 
                LIMIT 5
            """)
            previous_chats = cursor.fetchall()
            previous_chats.reverse()

            cursor.close()
            conn.close()
        except Exception as e:
            print("DB Fetch Error:", e)

        # Build context
        context_text = SYSTEM_PROMPT + "\n\n"

        for u, b in previous_chats:
            context_text += f"User: {u}\nGF: {b}\n"

        context_text += f"User: {user_message}\nGF:"

        # =========================
        # GOOGLE RESPONSE
        # =========================

        try:
            response = google_model.generate_content(
                context_text,
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": 120,
                }
            )

            full_reply = response.text.strip()

        except Exception as google_error:
            print("Google Error:", google_error)
            full_reply = "Hmm… thoda glitch ho gaya 😅 phir se bolo na"

        # Save to DB
        try:
            conn_save = psycopg2.connect(
                DATABASE_URL,
                sslmode="require",
                connect_timeout=10
            )
            cursor_save = conn_save.cursor()

            cursor_save.execute(
                "INSERT INTO chats (user_message, bot_reply) VALUES (%s, %s)",
                (user_message, full_reply)
            )

            conn_save.commit()
            cursor_save.close()
            conn_save.close()

        except Exception as e:
            print("DB Save Error:", e)

        return jsonify({"reply": full_reply})

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"reply": "Baby thoda network issue aa gaya 😔 try again"})


# =========================
# Run App (Local Only)
# =========================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
