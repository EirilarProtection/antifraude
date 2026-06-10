from flask import Flask, render_template, request, redirect, session, url_for, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_connection

app = Flask(__name__)
app.secret_key = "9f3K!xQ7vL2mR8sT6pZ4aN1dC"


# ==========================
# LOGIN
# ==========================
@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

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

        if user and user[1] and check_password_hash(user[1], password):
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

        username = request.form.get("username")
        password_raw = request.form.get("password")
        email = request.form.get("email")
        phone = request.form.get("phone")
        birthdate = request.form.get("birthdate")

        # validação básica
        if not username or not password_raw:
            return render_template("register.html", error="Preencha usuário e senha")

        password = generate_password_hash(password_raw)

        conn = get_connection()
        cur = conn.cursor()

        try:
            # verifica usuário existente
            cur.execute("SELECT id FROM users WHERE username=%s", (username,))
            exists = cur.fetchone()

            if exists:
                return render_template("register.html", error="Usuário já existe")

            # INSERÇÃO
            cur.execute("""
                INSERT INTO users (username, password_hash, role, email, phone, birthdate)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (username, password, "admin", email, phone, birthdate))

            conn.commit()

        except Exception as e:
            print("ERRO REGISTER:", e)
            return render_template("register.html", error="Erro ao criar conta")

        finally:
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

    cur.execute("""
        SELECT id, order_number, customer_name, amount, status, created_at
        FROM orders
        ORDER BY id DESC
        LIMIT 100
    """)

    orders = cur.fetchall()

    cur.execute("SELECT COUNT(*) FROM orders")
    total_orders = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM orders WHERE status = 'Aprovado'")
    approved = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM orders WHERE status = 'Suspeito'")
    alerts = cur.fetchone()[0]

    stats = {
        "orders": total_orders,
        "approved": approved,
        "alerts": alerts,
        "blocked_ips": 0,
        "blocked_devices": 0
    }

    cur.close()
    conn.close()

    return render_template("dashboard.html", stats=stats, orders=orders)


# ==========================
# APPROVE
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
# BLOCK
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

    data = request.json or {}

    cpf = data.get("cpf", "")
    email = data.get("email", "")
    ip = data.get("ip_address", "")
    amount = float(data.get("amount", 0))

    score = 0

    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("SELECT 1 FROM blacklist_cpfs WHERE cpf=%s", (cpf,))
        if cur.fetchone():
            score += 100

        cur.execute("SELECT 1 FROM blacklist_emails WHERE email=%s", (email,))
        if cur.fetchone():
            score += 80

        cur.execute("SELECT 1 FROM blacklist_ips WHERE ip=%s", (ip,))
        if cur.fetchone():
            score += 80

    except Exception as e:
        print("ERRO API:", e)

    if amount > 2000:
        score += 20
    if amount > 5000:
        score += 30

    if score >= 80:
        status = "Suspeito"
    elif score >= 40:
        status = "Revisão"
    else:
        status = "Aprovado"

    cur.close()
    conn.close()

    return jsonify({"score": score, "status": status})


# ==========================
# START
# ==========================
if __name__ == "__main__":
    app.run(debug=True)
