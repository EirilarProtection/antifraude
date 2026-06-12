import os
from flask import Flask, render_template
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

# =========================
# DATABASE
# =========================
DB_URL = os.getenv("DATABASE_URL")

def get_conn():
    return psycopg2.connect(DB_URL, cursor_factory=RealDictCursor)


# =========================
# STATS QUERY (DASHBOARD)
# =========================
def get_stats():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM users")
    users = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM orders")
    orders = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM login_history")
    logins = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM audit_logs")
    logs = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM blacklist")
    blacklist = cur.fetchone()[0]

    cur.close()
    conn.close()

    return {
        "users": users,
        "orders": orders,
        "logins": logins,
        "logs": logs,
        "blocked": blacklist,
        "high_risk": 0,
        "vpn": 0,
        "alerts": logs
    }


# =========================
# USERS LIST (RISK TABLE)
# =========================
def get_users():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, full_name, city, risk_score
        FROM users
        ORDER BY risk_score DESC NULLS LAST
        LIMIT 50
    """)

    users = cur.fetchall()
    cur.close()
    conn.close()

    return users


# =========================
# ALERTS (AUDIT LOGS)
# =========================
def get_alerts():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT action, details, created_at
        FROM audit_logs
        ORDER BY created_at DESC
        LIMIT 10
    """)

    alerts = cur.fetchall()
    cur.close()
    conn.close()

    return alerts


# =========================
# DASHBOARD ROUTE
# =========================
@app.route("/")
def dashboard():
    try:
        stats = get_stats()
        users = get_users()
        alerts = get_alerts()

        return render_template(
            "dashboard.html",
            stats=stats,
            users=users,
            alerts=alerts
        )

    except Exception as e:
        return f"Erro no dashboard: {str(e)}"


# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
