import os
from flask import Flask, render_template
from sqlalchemy import create_engine, text

app = Flask(__name__)

# 🔐 DATABASE DO RAILWAY
DB_URL = os.getenv("DATABASE_URL")

# 🔧 correção obrigatória do postgres
if DB_URL.startswith("postgresql://"):
    DB_URL = DB_URL.replace("postgresql://", "postgresql+psycopg2://")

engine = create_engine(DB_URL, pool_pre_ping=True)

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
