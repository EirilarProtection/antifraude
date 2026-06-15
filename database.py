import os
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.getenv("DATABASE_URL")

# =========================
# CONEXÃO
# =========================
def get_conn():
    return psycopg2.connect(
        DATABASE_URL,
        cursor_factory=RealDictCursor
    )

# =========================
# USERS
# =========================
def get_users():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT * FROM users ORDER BY id DESC")
    data = cur.fetchall()

    cur.close()
    conn.close()
    return data

# =========================
# ORDERS (fallback seguro)
# =========================
def get_orders(limit=50):
    conn = get_conn()
    cur = conn.cursor()

    # fallback: usando login_history como "atividade"
    cur.execute("""
        SELECT *
        FROM login_history
        ORDER BY login_date DESC
        LIMIT %s
    """, (limit,))

    data = cur.fetchall()

    cur.close()
    conn.close()
    return data

# =========================
# FRAUD EVENTS
# =========================
def get_fraud_events():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT * FROM fraud_events ORDER BY created_at DESC")
    data = cur.fetchall()

    cur.close()
    conn.close()
    return data

# =========================
# ALERTS
# =========================
def get_alerts():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT * FROM fraud_alerts ORDER BY created_at DESC")
    data = cur.fetchall()

    cur.close()
    conn.close()
    return data

# =========================
# DASHBOARD STATS (CORRIGIDO)
# =========================
def get_dashboard_stats():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM users")
    users = cur.fetchone()["count"]

    cur.execute("SELECT COUNT(*) FROM login_history")
    orders = cur.fetchone()["count"]

    cur.execute("SELECT COUNT(*) FROM fraud_events")
    frauds = cur.fetchone()["count"]

    cur.execute("SELECT COUNT(*) FROM fraud_alerts")
    alerts = cur.fetchone()["count"]

    cur.execute("SELECT COUNT(*) FROM active_sessions")
    sessions = cur.fetchone()["count"]

    cur.execute("""
        SELECT COUNT(*)
        FROM users
        WHERE blocked = true
    """)
    blocked = cur.fetchone()["count"]

    cur.execute("""
        SELECT COALESCE(AVG(risk_score), 0)
        FROM users
    """)
    avg_risk = cur.fetchone()["coalesce"]

    cur.close()
    conn.close()

    return {
        "total_users": users,
        "total_orders": orders,
        "total_frauds": frauds,
        "total_alerts": alerts,
        "total_sessions": sessions,
        "blocked_users": blocked,
        "avg_risk": round(avg_risk, 2)
    }
