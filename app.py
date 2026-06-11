from flask import Flask, render_template, request, redirect, session, url_for, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_connection

app = Flask(__name__)
app.secret_key = "9f3K!xQ7vL2mR8sT6pZ4aN1dC"


# ======================
# LOGIN
# ======================
@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "SELECT username, password_hash FROM users WHERE username=%s",
            (username,)
        )

        user = cur.fetchone()

        cur.close()
        conn.close()

        if user and check_password_hash(user[1], password):
            session["user"] = user[0]
            return redirect(url_for("dashboard"))

        return render_template(
            "login.html",
            error="Usuário ou senha inválidos"
        )

    return render_template("login.html")


# ======================
# REGISTER
# ======================
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password_hash = generate_password_hash(
            request.form["password"]
        )

        email = request.form.get("email")
        phone = request.form.get("phone")
        birthdate = request.form.get("birthdate")

        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "SELECT id FROM users WHERE username=%s",
            (username,)
        )

        if cur.fetchone():

            cur.close()
            conn.close()

            return render_template(
                "register.html",
                error="Usuário já existe"
            )

        cur.execute("""
            INSERT INTO users
            (
                username,
                password_hash,
                role,
                email,
                phone,
                birthdate
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
        """, (
            username,
            password_hash,
            "admin",
            email,
            phone,
            birthdate
        ))

        conn.commit()

        cur.close()
        conn.close()

        return redirect(url_for("login"))

    return render_template("register.html")


# ======================
# DASHBOARD
# ======================
@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect(url_for("login"))

    orders = []

    stats = {
        "orders": 0,
        "approved": 0,
        "alerts": 0,
        "blocked_ips": 0,
        "blocked_devices": 0
    }

    try:

        conn = get_connection()
        cur = conn.cursor()

        # PEDIDOS
        try:
            cur.execute(
                "SELECT * FROM orders ORDER BY id DESC LIMIT 50"
            )
            orders = cur.fetchall()

            stats["orders"] = len(orders)

        except Exception:
            orders = []

        # APROVADOS
        try:
            cur.execute(
                "SELECT COUNT(*) FROM orders WHERE status='Aprovado'"
            )
            stats["approved"] = cur.fetchone()[0]
        except Exception:
            pass

        # ALERTAS
        try:
            cur.execute(
                "SELECT COUNT(*) FROM orders WHERE status='Suspeito'"
            )
            stats["alerts"] = cur.fetchone()[0]
        except Exception:
            pass

        # IPS BLOQUEADOS
        try:
            cur.execute(
                "SELECT COUNT(*) FROM blacklist_ips"
            )
            stats["blocked_ips"] = cur.fetchone()[0]
        except Exception:
            pass

        # DEVICES BLOQUEADOS
        try:
            cur.execute(
                "SELECT COUNT(*) FROM blocked_devices"
            )
            stats["blocked_devices"] = cur.fetchone()[0]
        except Exception:
            pass

        cur.close()
        conn.close()

    except Exception:
        pass

    return render_template(
        "dashboard.html",
        orders=orders,
        stats=stats
    )


# ======================
# LOGOUT
# ======================
@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


# ======================
# API ANTIFRAUDE
# ======================
@app.route("/api/analyze", methods=["POST"])
def analyze():

    data = request.json or {}

    cpf = data.get("cpf", "")
    email = data.get("email", "")
    ip = data.get("ip_address", "")
    amount = float(data.get("amount", 0))

    score = 0

    try:

        conn = get_connection()
        cur = conn.cursor()

        try:
            cur.execute(
                "SELECT 1 FROM blacklist_cpfs WHERE cpf=%s",
                (cpf,)
            )

            if cur.fetchone():
                score += 100

        except:
            pass

        try:
            cur.execute(
                "SELECT 1 FROM blacklist_emails WHERE email=%s",
                (email,)
            )

            if cur.fetchone():
                score += 80

        except:
            pass

        try:
            cur.execute(
                "SELECT 1 FROM blacklist_ips WHERE ip=%s",
                (ip,)
            )

            if cur.fetchone():
                score += 80

        except:
            pass

        cur.close()
        conn.close()

    except:
        pass

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

    return jsonify({
        "score": score,
        "status": status
    })


# ======================
# START
# ======================
if __name__ == "__main__":
    app.run(debug=True)
