import os
from flask import Flask
from sqlalchemy import create_engine

app = Flask(__name__)

DB_URL = os.getenv("DATABASE_URL")

if not DB_URL:
    raise Exception("DATABASE_URL não configurada no Railway")

if not DB_URL.startswith("postgresql://"):
    raise Exception("DATABASE_URL inválida")

engine = create_engine(DB_URL, pool_pre_ping=True)

print("Banco conectado com sucesso")

# ---------------- DASHBOARD ----------------
@app.route("/")
def dashboard():

    with engine.connect() as conn:

        users = conn.execute(text("SELECT * FROM users ORDER BY id DESC LIMIT 10")).mappings().all()

        stats = {
            "users": conn.execute(text("SELECT COUNT(*) FROM users")).scalar(),
            "orders": conn.execute(text("SELECT COUNT(*) FROM orders")).scalar(),
            "logs": conn.execute(text("SELECT COUNT(*) FROM audit_logs")).scalar(),
            "login_history": conn.execute(text("SELECT COUNT(*) FROM login_history")).scalar(),
            "notes": conn.execute(text("SELECT COUNT(*) FROM user_notes")).scalar(),

            # extras
            "high_risk": conn.execute(text("SELECT COUNT(*) FROM users WHERE risk_score >= 70")).scalar(),
            "blocked": conn.execute(text("SELECT COUNT(*) FROM users WHERE account_status = 'blocked'")).scalar(),
            "vpn": conn.execute(text("SELECT COUNT(*) FROM users WHERE vpn_detected = true")).scalar(),
            "alerts": conn.execute(text("SELECT COUNT(*) FROM audit_logs")).scalar(),
        }

        alerts = conn.execute(text("""
            SELECT action, details, created_at
            FROM audit_logs
            ORDER BY created_at DESC
            LIMIT 5
        """)).mappings().all()

    return render_template(
        "dashboard.html",
        stats=stats,
        users=users,
        alerts=alerts
    )


# ---------------- START ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
