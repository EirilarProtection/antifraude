from flask import Flask, render_template
import psycopg2
import os

app = Flask(__name__)

# 🔐 Use variável de ambiente (RECOMENDADO)
# no Railway: DATABASE_URL
DB_URL = os.getenv("DATABASE_URL")

def get_conn():
    return psycopg2.connect(DB_URL)

# ---------------- DASHBOARD ----------------
@app.route("/")
def dashboard():
    conn = get_conn()
    cur = conn.cursor()

    # USERS (painel principal)
    cur.execute("""
        SELECT id, full_name, city, risk_score, account_status, vpn_detected
        FROM users
        ORDER BY risk_score DESC
    """)
    users = [
        {
            "id": r[0],
            "full_name": r[1],
            "city": r[2],
            "risk_score": r[3],
            "account_status": r[4],
            "vpn_detected": r[5]
        }
        for r in cur.fetchall()
    ]

    # STATS
    cur.execute("SELECT COUNT(*) FROM users")
    users_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM orders")
    orders_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM users WHERE risk_score >= 70")
    high_risk = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM users WHERE account_status = 'Bloqueado'")
    blocked = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM users WHERE vpn_detected = TRUE")
    vpn = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM audit_logs")
    alerts = cur.fetchone()[0]

    # ALERTAS (central de risco)
    cur.execute("""
        SELECT action, details, created_at
        FROM audit_logs
        ORDER BY id DESC
        LIMIT 10
    """)
    alerts_list = [
        {
            "action": r[0],
            "details": r[1],
            "created_at": r[2]
        }
        for r in cur.fetchall()
    ]

    conn.close()

    return render_template(
        "dashboard.html",
        users=users,
        alerts=alerts_list,
        stats={
            "users": users_count,
            "orders": orders_count,
            "high_risk": high_risk,
            "blocked": blocked,
            "vpn": vpn,
            "alerts": alerts
        }
    )


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
