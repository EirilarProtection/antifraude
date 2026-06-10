from flask import Flask, render_template, request, redirect, session, url_for, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_connection

app = Flask(__name__)
app.secret_key = "troque_essa_chave_agora"


# ==========================
# LOGIN
# ==========================
@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT username, password_hash
            FROM users
            WHERE username = %s
        """, (username,))

        user = cur.fetchone()

        cur.close()
        conn.close()

        if user and check_password_hash(user[1], password):
            session["user"] = user[0]
            return redirect(url_for("dashboard"))

        return render_template("login.html", error="Usuário ou senha inválidos")

    return render_template("login.html")


# ==========================
# REGISTER
# ==========================
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = generate_password_hash(request.form["password"])
        email = request.form["email"]

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT id FROM users WHERE username=%s", (username,))
        exists = cur.fetchone()

        if exists:
            cur.close()
            conn.close()
            return render_template("register.html", error="Usuário já existe")

        cur.execute("""
            INSERT INTO users (username, password_hash, role)
            VALUES (%s, %s, %s)
        """, (username, password, "admin"))

        conn.commit()

        cur.close()
        conn.close()

        return redirect(url_for("login"))

    return render_template("register.html")


# ==========================
# DASHBOARD
# ==========================
@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cur = conn.cursor()

    # Orders
    cur.execute("""
        SELECT *
        FROM orders
        ORDER BY id DESC
        LIMIT 100
    """)
    orders = cur.fetchall()

    # Stats
    cur.execute("SELECT COUNT(*) FROM orders")
    total_orders = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM orders WHERE status = 'Aprovado'")
    approved = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM orders WHERE status = 'Suspeito'")
    alerts = cur.fetchone()[0]

    cur.execute("SELECT COUNT(DISTINCT ip_address) FROM orders")
    ips = cur.fetchone()[0]

    stats = {
        "orders": total_orders,
        "approved": approved,
        "alerts": alerts,
        "blocked_ips": ips,
        "blocked_devices": 0
    }

    cur.close()
    conn.close()

    return render_template(
        "dashboard.html",
        stats=stats,
        orders=orders
    )


# ==========================
# APPROVE ORDER
# ==========================
@app.route("/approve/<int:order_id>")
def approve(order_id):

    if "user" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE orders
        SET status = 'Aprovado'
        WHERE id = %s
    """, (order_id,))

    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for("dashboard"))


# ==========================
# BLOCK ORDER
# ==========================
@app.route("/block/<int:order_id>")
def block(order_id):

    if "user" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE orders
        SET status = 'Suspeito'
        WHERE id = %s
    """, (order_id,))

    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for("dashboard"))


# ==========================
# LOGOUT
# ==========================
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ==========================
# API ANTIFRAUDE
# ==========================
@app.route("/api/analyze", methods=["POST"])
def analyze():

    data = request.json

    score = 0

    conn = get_connection()
    cur = conn.cursor()

    # BLACKLIST CPF
    cur.execute("SELECT id FROM blacklist_cpfs WHERE cpf=%s", (data["cpf"],))
    if cur.fetchone():
        score += 100

    # BLACKLIST EMAIL
    cur.execute("SELECT id FROM blacklist_emails WHERE email=%s", (data["email"],))
    if cur.fetchone():
        score += 80

    # BLACKLIST IP
    cur.execute("SELECT id FROM blacklist_ips WHERE ip=%s", (data["ip_address"],))
    if cur.fetchone():
        score += 80

    # RULES SIMPLES
    if data["amount"] > 2000:
        score += 20

    if data["amount"] > 5000:
        score += 30

    # RESULTADO FINAL
    if score >= 80:
        status = "Suspeito"
    elif score >= 40:
        status = "Revisão"
    else:
        status = "Aprovado"

    cur.close()
    conn.close()

    return jsonify({
        "score": score,
        "status": status
    })


# ==========================
# START
# ==========================
if __name__ == "__main__":
    app.run(debug=True)
