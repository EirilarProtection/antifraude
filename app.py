import os
from flask import Flask, render_template
from sqlalchemy import create_engine, text

app = Flask(__name__)

# pegar variável do Railway
DB_URL = os.environ.get("DATABASE_URL")

# validação segura (NUNCA deixa None quebrar o app)
if not DB_URL:
    raise Exception("DATABASE_URL não encontrada no ambiente do Railway")

# Railway às vezes usa postgres:// -> corrigir para SQLAlchemy
if DB_URL.startswith("postgres://"):
    DB_URL = DB_URL.replace("postgres://", "postgresql://")

engine = create_engine(DB_URL, pool_pre_ping=True)

@app.route("/")
def dashboard():
    return render_template("dashboard.html")


@app.route("/health")
def health():
    return {"status": "ok"}
