import os
from flask import Flask, render_template, request, jsonify
from sqlalchemy import create_engine, text
from datetime import datetime

app = Flask(__name__)

# =========================
# DATABASE RAILWAY
# =========================
DB_URL = os.getenv("DATABASE_URL")

if not DB_URL:
    raise Exception("DATABASE_URL não configurada no Railway")

# compatibilidade Railway
if DB_URL.startswith("postgres://"):
    DB_URL = DB_URL.replace("postgres://", "postgresql://")

engine = create_engine(DB_URL, pool_pre_ping=True)

# =========================
# INIT DB (cria tabela se não existir)
# =========================
def init_db():
    with engine.begin() as conn:
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS logs (
            id SERIAL PRIMARY KEY,
            ip TEXT,
            user_agent TEXT,
            path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """))

init_db()


# =========================
# MIDDLEWARE ANTIFRAUDE SIMPLES
# =========================
@app.before_request
def log_request():
    try:
        ip = request.headers.get("X-Forwarded-For", request.remote_addr)
        ua = request.headers.get("User-Agent")
        path = request.path

        with engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO logs (ip, user_agent, path)
                VALUES (:ip, :ua, :path)
            """), {"ip": ip, "ua": ua, "path": path})

    except Exception as e:
        print("Erro log:", e)


# =========================
# DASHBOARD
# =========================
@app.route("/")
def dashboard():
    with engine.connect() as conn:
        logs = conn.execute(text("""
            SELECT * FROM logs
            ORDER BY id DESC
            LIMIT 50
        """)).fetchall()

    return render_template("dashboard.html", logs=logs)


# =========================
# API STATUS
# =========================
@app.route("/api/status")
def status():
    return jsonify({
        "status": "ok",
        "time": str(datetime.utcnow())
    })


# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
