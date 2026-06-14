from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session,
    jsonify
)

from database import get_conn

app = Flask(__name__)
app.secret_key = "CHANGE_THIS_SECRET"


# ==================================================
# HOME
# ==================================================
@app.route("/")
def home():

    if "user_id" in session:
        return redirect("/dashboard")

    return redirect("/login")


# ==================================================
# REGISTER
# ==================================================
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"].strip()
        first_name = request.form["first_name"].strip()
        last_name = request.form["last_name"].strip()
        email = request.form["email"].strip()
        birthdate = request.form["birthdate"]
        password = request.form["password"]

        full_name = f"{first_name} {last_name}"

        conn = get_conn()
        cur = conn.cursor()

        try:

            # username único
            cur.execute(
                """
                SELECT id
                FROM users
                WHERE username = %s
                """,
                (username,)
            )

            existing_user = cur.fetchone()

            if existing_user:
                return render_template(
                    "register.html",
                    error="Usuário já existe."
                )

            cur.execute(
                """
                INSERT INTO users
                (
                    username,
                    email,
                    full_name,
                    birthdate,
                    password_hash,
                    risk_score,
                    risk_level,
                    account_status,
                    failed_logins,
                    login_count,
                    vpn_detected,
                    trusted_user,
                    fraud_attempts,
                    email_verified,
                    phone_verified,
                    created_at
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    0,
                    'Baixo',
                    'Ativo',
                    0,
                    0,
                    FALSE,
                    FALSE,
                    0,
                    FALSE,
                    FALSE,
                    NOW()
                )
                """,
                (
                    username,
                    email,
                    full_name,
                    birthdate,
                    password
                )
            )

            conn.commit()

            return redirect("/login")

        finally:
            cur.close()
            conn.close()

except Exception as e:
    print("ERRO REGISTER:", e)
    return render_template("register.html", error=str(e))


# ==================================================
# LOGIN
# ==================================================
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        login_value = request.form["email"].strip()
        password = request.form["password"]

        conn = get_conn()
        cur = conn.cursor()

        try:
            cur.execute("""
                SELECT id, username FROM users
                WHERE (email=%s OR username=%s)
                AND password_hash=%s
            """, (login_value, login_value, password))

            user = cur.fetchone()

            if user:
                session["user_id"] = user[0]
                session["username"] = user[1]
                return redirect("/dashboard")

            return render_template("login.html", error="Login inválido")

        except Exception as e:
            print("ERRO LOGIN:", e)
            return render_template("login.html", error=str(e))

        finally:
            cur.close()
            conn.close()

    return render_template("login.html")


# ==================================================
# LOGOUT
# ==================================================
@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")

# ==================================================
# DASHBOARD
# ==================================================
@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect("/login")

    return render_template(
        "dashboard.html",
        username=session.get("username")
    )


# ==================================================
# API STATS (PAINEL PRINCIPAL)
# ==================================================
@app.route("/api/stats")
def stats():

    if "user_id" not in session:
        return jsonify({"error": "unauthorized"}), 401

    conn = get_conn()
    cur = conn.cursor()

    try:

        # USERS
        cur.execute("SELECT COUNT(*) FROM users")
        users = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM login_history")
        logins = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM orders")
        orders = cur.fetchone()[0]

        # RISK
        cur.execute("SELECT COUNT(*) FROM users WHERE risk_level = 'Alto'")
        high_risk = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM users WHERE account_status = 'Bloqueado'")
        blocked_users = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM orders WHERE status = 'Suspeito'")
        suspicious_orders = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM orders WHERE status = 'Bloqueado'")
        blocked_orders = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM orders WHERE fraud_flag = true")
        fraud_orders = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM orders WHERE review_required = true")
        review_orders = cur.fetchone()[0]

        # BLACKLIST
        cur.execute("SELECT COUNT(*) FROM blacklist")
        blacklist = cur.fetchone()[0]

        # FRAUD RULES
        cur.execute("SELECT COUNT(*) FROM fraud_rules WHERE active = true")
        fraud_rules = cur.fetchone()[0]

        return jsonify({
            "users": users,
            "logins": logins,
            "orders": orders,

            "high_risk": high_risk,
            "blocked_users": blocked_users,

            "suspicious_orders": suspicious_orders,
            "blocked_orders": blocked_orders,
            "fraud_orders": fraud_orders,
            "review_orders": review_orders,

            "blacklist": blacklist,
            "fraud_rules": fraud_rules
        })

    finally:
        cur.close()
        conn.close()

# ==================================================
# API USERS
# ==================================================
@app.route("/api/users")
def api_users():

    if "user_id" not in session:
        return jsonify([])

    conn = get_conn()
    cur = conn.cursor()

    try:

        cur.execute("""
            SELECT
                id,
                username,
                email,
                full_name,
                risk_score,
                risk_level,
                account_status,
                login_count,
                vpn_detected,
                last_ip
            FROM users
            ORDER BY id DESC
            LIMIT 100
        """)

        rows = cur.fetchall()

        return jsonify([
            {
                "id": r[0],
                "username": r[1],
                "email": r[2],
                "full_name": r[3],
                "risk_score": r[4],
                "risk_level": r[5],
                "status": r[6],
                "login_count": r[7],
                "vpn": r[8],
                "ip": r[9]
            }
            for r in rows
        ])

    finally:
        cur.close()
        conn.close()


# ==================================================
# API ORDERS
# ==================================================
@app.route("/api/orders")
def api_orders():

    if "user_id" not in session:
        return jsonify([])

    conn = get_conn()
    cur = conn.cursor()

    try:

        cur.execute("""
            SELECT
                id,
                client_name,
                amount,
                status,
                risk_score,
                payment_method,
                country,
                city,
                fraud_flag,
                review_required,
                created_at
            FROM orders
            ORDER BY id DESC
            LIMIT 100
        """)

        rows = cur.fetchall()

        return jsonify([
            {
                "id": r[0],
                "client": r[1],
                "amount": float(r[2]),
                "status": r[3],
                "risk": r[4],
                "payment": r[5],
                "country": r[6],
                "city": r[7],
                "fraud": r[8],
                "review": r[9],
                "date": str(r[10])
            }
            for r in rows
        ])

    finally:
        cur.close()
        conn.close()


# ==================================================
# API LOGIN HISTORY
# ==================================================
@app.route("/api/logins")
def api_logins():

    if "user_id" not in session:
        return jsonify([])

    conn = get_conn()
    cur = conn.cursor()

    try:

        cur.execute("""
            SELECT
                user_id,
                ip_address,
                country,
                city,
                browser,
                operating_system,
                login_date
            FROM login_history
            ORDER BY login_date DESC
            LIMIT 50
        """)

        rows = cur.fetchall()

        return jsonify([
            {
                "user_id": r[0],
                "ip": r[1],
                "country": r[2],
                "city": r[3],
                "browser": r[4],
                "os": r[5],
                "date": str(r[6])
            }
            for r in rows
        ])

    finally:
        cur.close()
        conn.close()


# ==================================================
# API BLACKLIST
# ==================================================
@app.route("/api/blacklist")
def api_blacklist():

    if "user_id" not in session:
        return jsonify([])

    conn = get_conn()
    cur = conn.cursor()

    try:

        cur.execute("""
            SELECT
                id,
                type,
                value,
                reason,
                created_at
            FROM blacklist
            ORDER BY id DESC
        """)

        rows = cur.fetchall()

        return jsonify([
            {
                "id": r[0],
                "type": r[1],
                "value": r[2],
                "reason": r[3],
                "date": str(r[4])
            }
            for r in rows
        ])

    finally:
        cur.close()
        conn.close()


# ==================================================
# API FRAUD RULES
# ==================================================
@app.route("/api/fraud-rules")
def api_fraud_rules():

    if "user_id" not in session:
        return jsonify([])

    conn = get_conn()
    cur = conn.cursor()

    try:

        cur.execute("""
            SELECT
                id,
                rule_name,
                points,
                active
            FROM fraud_rules
            ORDER BY id DESC
        """)

        rows = cur.fetchall()

        return jsonify([
            {
                "id": r[0],
                "name": r[1],
                "points": r[2],
                "active": r[3]
            }
            for r in rows
        ])

    finally:
        cur.close()
        conn.close()


# ==================================================
# API AUDIT LOGS
# ==================================================
@app.route("/api/audit-logs")
def api_audit_logs():

    if "user_id" not in session:
        return jsonify([])

    conn = get_conn()
    cur = conn.cursor()

    try:

        cur.execute("""
            SELECT
                id,
                user_id,
                action,
                details,
                created_at
            FROM audit_logs
            ORDER BY created_at DESC
            LIMIT 100
        """)

        rows = cur.fetchall()

        return jsonify([
            {
                "id": r[0],
                "user_id": r[1],
                "action": r[2],
                "details": r[3],
                "date": str(r[4])
            }
            for r in rows
        ])

    finally:
        cur.close()
        conn.close()


# ==================================================
# API USER NOTES
# ==================================================
@app.route("/api/user-notes")
def api_user_notes():

    if "user_id" not in session:
        return jsonify([])

    conn = get_conn()
    cur = conn.cursor()

    try:

        cur.execute("""
            SELECT
                id,
                user_id,
                admin_name,
                note,
                created_at
            FROM user_notes
            ORDER BY created_at DESC
        """)

        rows = cur.fetchall()

        return jsonify([
            {
                "id": r[0],
                "user_id": r[1],
                "admin": r[2],
                "note": r[3],
                "date": str(r[4])
            }
            for r in rows
        ])

    finally:
        cur.close()
        conn.close()
