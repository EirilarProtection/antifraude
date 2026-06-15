import os
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.getenv("DATABASE_URL")

def get_conn():
return psycopg2.connect(
DATABASE_URL,
cursor_factory=RealDictCursor
)

# ==================================================

# USERS

# ==================================================

def get_users():
conn = get_conn()
cur = conn.cursor()

```
cur.execute("""
    SELECT *
    FROM users
    ORDER BY id DESC
""")

data = cur.fetchall()

cur.close()
conn.close()

return data
```

def get_user(user_id):
conn = get_conn()
cur = conn.cursor()

```
cur.execute("""
    SELECT *
    FROM users
    WHERE id = %s
""", (user_id,))

data = cur.fetchone()

cur.close()
conn.close()

return data
```

# ==================================================

# ORDERS

# ==================================================

def get_orders(limit=100):
conn = get_conn()
cur = conn.cursor()

```
cur.execute("""
    SELECT *
    FROM orders
    ORDER BY created_at DESC
    LIMIT %s
""", (limit,))

data = cur.fetchall()

cur.close()
conn.close()

return data
```

# ==================================================

# FRAUD EVENTS

# ==================================================

def get_fraud_events(limit=100):
conn = get_conn()
cur = conn.cursor()

```
cur.execute("""
    SELECT *
    FROM fraud_events
    ORDER BY created_at DESC
    LIMIT %s
""", (limit,))

data = cur.fetchall()

cur.close()
conn.close()

return data
```

# ==================================================

# FRAUD RULES

# ==================================================

def get_fraud_rules():
conn = get_conn()
cur = conn.cursor()

```
cur.execute("""
    SELECT *
    FROM fraud_rules
    ORDER BY id DESC
""")

data = cur.fetchall()

cur.close()
conn.close()

return data
```

# ==================================================

# ALERTS

# ==================================================

def get_alerts():
conn = get_conn()
cur = conn.cursor()

```
cur.execute("""
    SELECT *
    FROM fraud_alerts
    ORDER BY created_at DESC
""")

data = cur.fetchall()

cur.close()
conn.close()

return data
```

# ==================================================

# NOTIFICATIONS

# ==================================================

def get_notifications():
conn = get_conn()
cur = conn.cursor()

```
cur.execute("""
    SELECT *
    FROM notifications
    ORDER BY created_at DESC
""")

data = cur.fetchall()

cur.close()
conn.close()

return data
```

# ==================================================

# LOGIN HISTORY

# ==================================================

def get_login_history(limit=100):
conn = get_conn()
cur = conn.cursor()

```
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
```

# ==================================================

# DEVICES

# ==================================================

def get_devices():
conn = get_conn()
cur = conn.cursor()

```
cur.execute("""
    SELECT *
    FROM devices
    ORDER BY created_at DESC
""")

data = cur.fetchall()

cur.close()
conn.close()

return data
```

# ==================================================

# GEO TRACKING

# ==================================================

def get_geo_tracking():
conn = get_conn()
cur = conn.cursor()

```
cur.execute("""
    SELECT *
    FROM geo_tracking
    ORDER BY created_at DESC
""")

data = cur.fetchall()

cur.close()
conn.close()

return data
```

# ==================================================

# BLACKLIST

# ==================================================

def get_blacklist():
conn = get_conn()
cur = conn.cursor()

```
cur.execute("""
    SELECT *
    FROM blacklist_items
    ORDER BY created_at DESC
""")

data = cur.fetchall()

cur.close()
conn.close()

return data
```

# ==================================================

# AUDIT LOGS

# ==================================================

def get_audit_logs():
conn = get_conn()
cur = conn.cursor()

```
cur.execute("""
    SELECT *
    FROM audit_logs
    ORDER BY created_at DESC
""")

data = cur.fetchall()

cur.close()
conn.close()

return data
```

# ==================================================

# ACTIVE SESSIONS

# ==================================================

def get_active_sessions():
conn = get_conn()
cur = conn.cursor()

```
cur.execute("""
    SELECT *
    FROM active_sessions
    ORDER BY ultimo_acesso DESC
""")

data = cur.fetchall()

cur.close()
conn.close()

return data
```

# ==================================================

# REPORTS

# ==================================================

def get_reports():
conn = get_conn()
cur = conn.cursor()

```
cur.execute("""
    SELECT *
    FROM reports
    ORDER BY created_at DESC
""")

data = cur.fetchall()

cur.close()
conn.close()

return data
```

# ==================================================

# SYSTEM SETTINGS

# ==================================================

def get_settings():
conn = get_conn()
cur = conn.cursor()

```
cur.execute("""
    SELECT *
    FROM system_settings
    ORDER BY id ASC
""")

data = cur.fetchall()

cur.close()
conn.close()

return data
```

# ==================================================

# DASHBOARD STATS

# ==================================================

def get_dashboard_stats():

```
conn = get_conn()
cur = conn.cursor()

cur.execute("SELECT COUNT(*) total FROM users")
users = cur.fetchone()["total"]

cur.execute("SELECT COUNT(*) total FROM orders")
orders = cur.fetchone()["total"]

cur.execute("SELECT COUNT(*) total FROM fraud_events")
frauds = cur.fetchone()["total"]

cur.execute("SELECT COUNT(*) total FROM fraud_alerts")
alerts = cur.fetchone()["total"]

cur.execute("SELECT COUNT(*) total FROM active_sessions")
sessions = cur.fetchone()["total"]

cur.execute("""
    SELECT COUNT(*) total
    FROM users
    WHERE account_status='Bloqueado'
""")
blocked = cur.fetchone()["total"]

cur.close()
conn.close()

return {
    "users": users,
    "orders": orders,
    "frauds": frauds,
    "alerts": alerts,
    "sessions": sessions,
    "blocked": blocked
}
```
