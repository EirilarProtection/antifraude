from flask import Flask, render_template, request, redirect, session, jsonify
from database import get_conn
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev_secret_123")


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
        try:
            username = request.form["username"]
            first_name = request.form["first_name"]
            last_name = request.form["last_name"]
            email = request.form["email"]
            birthdate = request.form["birthdate"]
            password = request.form["password"]

            full_name = f"{first_name} {last_name}"

            conn = get_conn()
            cur = conn.cursor()

            cur.execute("""
                SELECT id FROM users
                WHERE username=%s OR email=%s
            """, (username, email))

            if cur.fetchone():
                return render_template("register.html", error="Usuário ou email já existe")

            cur.execute("""
                INSERT INTO users (
                    username, email, full_name, birthdate,
                    password_hash,
                    risk_score, risk_level,
                    account_status,
                    failed_logins, login_count,
                    vpn_detected, trusted_user,
                    fraud_attempts,
                    email_verified, phone_verified,
                    created_at
                )
                VALUES (
                    %s,%s,%s,%s,%s,
                    0,'Baixo','Ativo',
                    0,0,
                    FALSE,FALSE,
                    0,
                    FALSE,FALSE,
                    NOW()
                )
            """, (
                username, email, full_name, birthdate, password
            ))

            conn.commit()
            cur.close()
            conn.close()

            return redirect("/login")

        except Exception as e:
            print("ERRO REGISTER:", e)
            return render_template("register.html", error="Erro ao criar conta")

    return render_template("register.html")


# ==================================================
# LOGIN
# ==================================================
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        try:
            login_value = request.form["email"].strip()
            password = request.form["password"].strip()

            conn = get_conn()
            cur = conn.cursor()

            cur.execute("""
                SELECT id, username, password_hash
                FROM users
                WHERE email=%s OR username=%s
            """, (login_value, login_value))

            user = cur.fetchone()

            if user and str(user[2]).strip() == str(password):

                session["user_id"] = user[0]
                session["username"] = user[1]

                cur.execute("""
                    UPDATE users
                    SET login_count = login_count + 1
                    WHERE id = %s
                """, (user[0],))

                conn.commit()
                cur.close()
                conn.close()

                return redirect("/dashboard")

            cur.close()
            conn.close()

            return render_template("login.html", error="Login inválido")

        except Exception as e:
            print("ERRO LOGIN:", e)
            return render_template("login.html", error="Erro interno")

    return render_template("login.html")


# ==================================================
# DASHBOARD
# ==================================================
@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect("/login")

    return render_template("dashboard.html", username=session.get("username"))


# ==================================================
# STATS
# ==================================================
@app.route("/api/stats")
def stats():

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM users")
    users = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM login_history")
    logins = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM users WHERE risk_score > 70")
    risk = cur.fetchone()[0]

    return jsonify({
        "users": users,
        "logins": logins,
        "high_risk": risk
    })


# ==================================================
# USERS
# ==================================================
@app.route("/api/users")
def api_users():

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, username, email, risk_score, risk_level, account_status, login_count
        FROM users
        ORDER BY id DESC
    """)

    rows = cur.fetchall()

    return jsonify([
        {
            "id": r[0],
            "username": r[1],
            "email": r[2],
            "risk_score": r[3],
            "risk_level": r[4],
            "status": r[5],
            "login_count": r[6]
        }
        for r in rows
    ])


# ==================================================
# LOGINS (IPS + USERS)
# ==================================================
@app.route("/api/logins")
def logins():

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            l.id,
            u.username,
            l.ip_address,
            l.city,
            l.state,
            l.country,
            l.browser,
            l.operating_system,
            l.login_date
        FROM login_history l
        JOIN users u ON u.id = l.user_id
        ORDER BY l.login_date DESC
        LIMIT 50
    """)

    rows = cur.fetchall()

    return jsonify([
        {
            "id": r[0],
            "user": r[1],
            "ip": r[2],
            "city": r[3],
            "state": r[4],
            "country": r[5],
            "browser": r[6],
            "os": r[7],
            "date": str(r[8])
        }
        for r in rows
    ])


# ==================================================
# BLOCK USER
# ==================================================
@app.route("/api/block_user/<int:user_id>", methods=["POST"])
def block_user(user_id):

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        UPDATE users
        SET account_status = 'Bloqueado'
        WHERE id = %s
    """, (user_id,))

    conn.commit()
    return jsonify({"status": "blocked"})


# ==================================================
# UNBLOCK USER
# ==================================================
@app.route("/api/unblock_user/<int:user_id>", methods=["POST"])
def unblock_user(user_id):

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        UPDATE users
        SET account_status = 'Ativo'
        WHERE id = %s
    """, (user_id,))

    conn.commit()
    return jsonify({"status": "unblocked"})


# ==================================================
# NOTIFY USER
# ==================================================
@app.route("/api/notify_user/<int:user_id>", methods=["POST"])
def notify_user(user_id):

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO notifications (user_id, message)
        VALUES (%s, %s)
    """, (user_id, "Você recebeu uma notificação do sistema."))

    conn.commit()
    return jsonify({"status": "notified"})


# ==================================================
# USER DETAILS
# ==================================================
@app.route("/api/user/<int:user_id>")
def user_details(user_id):

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, username, email, risk_score, risk_level, account_status
        FROM users
        WHERE id = %s
    """, (user_id,))

    u = cur.fetchone()

    return jsonify({
        "id": u[0],
        "username": u[1],
        "email": u[2],
        "risk_score": u[3],
        "risk_level": u[4],
        "status": u[5]
    })


# ==================================================
# LOGOUT
# ==================================================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ==================================================
# START
# ==================================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
