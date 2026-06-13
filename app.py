import os
from flask import Flask, render_template, jsonify
from sqlalchemy import create_engine

app = Flask(__name__)

# pega variável de ambiente
DB_URL = os.getenv("DATABASE_URL")

# Railway já fornece isso, mas às vezes o Gunicorn inicia antes do env carregar corretamente
if not DB_URL:
    DB_URL = os.getenv("POSTGRES_URL") or os.getenv("DATABASE_PUBLIC_URL")

# se ainda não existir, NÃO derruba o app
if not DB_URL:
    print("⚠️ DATABASE_URL não encontrada. Rodando sem banco.")
    engine = None
else:
    # corrigir formato antigo
    if DB_URL.startswith("postgres://"):
        DB_URL = DB_URL.replace("postgres://", "postgresql://")

    engine = create_engine(DB_URL, pool_pre_ping=True)


@app.route("/")
def dashboard():
    return render_template("dashboard.html")


@app.route("/health")
def health():
    return {
        "status": "ok",
        "database": "connected" if engine else "missing"
    }


@app.route("/test-db")
def test_db():
    if not engine:
        return jsonify({"error": "sem conexão com banco"}), 500

    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return {"db": "ok"}
    except Exception as e:
        return {"db": "error", "detail": str(e)}
