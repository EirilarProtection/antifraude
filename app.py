from flask import Flask, render_template
import psycopg2
import os

app = Flask(__name__)

# 🔐 Railway usa variável de ambiente
DB_URL = os.getenv("postgresql://postgres:OfEYKNGiqqhUOhsNlwuYyxRzrMiiLsIj@acela.proxy.rlwy.net:22734/railway")

def get_conn():
    return psycopg2.connect(DB_URL)

# ---------------- DASHBOARD ----------------
@app.route("/")
def dashboard():

    conn = get_conn()
    cur = conn.cursor()

    # ---------------- USERS ----------------
    cur.execute("""
        SELECT
            id,
            COALESCE(full_name, username) as full_name,
            COALESCE(city, 'Unknown') as city,
            COALESCE(risk_score, 0) as risk_score
        FROM users
        ORDER BY risk_score DESC
        LIMIT 50
    """)

    users = [
        {
            "id": r[0],
            "full_name": r[1],
            "city": r[2],
            "risk_score": r[3]
        }
        for r in cur.fetchall()
    ]

    # ---------------- STATS ----------------
    cur.execute("SELECT COUNT(*) FROM users")
    users_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM orders")
    orders_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM users WHERE risk_score >= 70")
    high_risk = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*) 
        FROM users 
        WHERE account_status = 'blocked' OR account_status = 'Bloqueado'
    """)
    blocked = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*) 
        FROM users 
        WHERE vpn_detected = TRUE
    """)
    vpn = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM audit_logs")
    alerts = cur.fetchone()[0]

    # ---------------- ALERTS ----------------
    cur.execute("""
        SELECT 
            COALESCE(action, 'event'),
            COALESCE(details, 'no details')
        FROM audit_logs
        ORDER BY id DESC
        LIMIT 10
    """)

    alerts_list = [
        {
            "action": r[0],
            "details": r[1]
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


# ---------------- START SERVER ----------------
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
