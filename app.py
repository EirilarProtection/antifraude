from flask import Flask, render_template, request, redirect, session, url_for
import os
import psycopg2

app = Flask(__name__)
app.secret_key = "chave_super_secreta"

DATABASE_URL = os.getenv("DATABASE_URL")


# ------------------------
# CONEXÃO BANCO (RAILWAY)
# ------------------------
def get_connection():
    if not DATABASE_URL:
        raise Exception("DATABASE_URL não configurada no ambiente")

    return psycopg2.connect(DATABASE_URL, sslmode="require")


# ------------------------
# LOGIN
# ------------------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT username, password
            FROM users
            WHERE username = %s
        """, (username,))

        user = cur.fetchone()

        cur.close()
        conn.close()

        if user and user[1] == password:
            session["user"] = username
            return redirect(url_for("dashboard"))

        return render_template("login.html", error="Usuário ou senha inválidos")

    return render_template("login.html")


# ------------------------
# REGISTER
# ------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        email = request.form["email"]
        phone = request.form["phone"]
        birthdate = request.form["birthdate"]

        conn = get_connection()
        cur = conn.cursor()

        # verifica se existe
        cur.execute("SELECT username FROM users WHERE username = %s", (username,))
        exists = cur.fetchone()

        if exists:
            cur.close()
            conn.close()
            return render_template("register.html", error="Usuário já existe")

        # insere usuário
        cur.execute("""
            INSERT INTO users (username, password, email, phone, birthdate)
            VALUES (%s, %s, %s, %s, %s)
        """, (username, password, email, phone, birthdate))

        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for("login"))

    return render_template("register.html")


# ------------------------
# DASHBOARD (BANCO REAL)
# ------------------------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cur = conn.cursor()

    # pedidos reais do banco
    cur.execute("SELECT * FROM orders ORDER BY id DESC LIMIT 100;")

    columns = [desc[0] for desc in cur.description]
    orders = cur.fetchall()

    # dados do usuário logado
    cur.execute("""
        SELECT username, email, phone, birthdate
        FROM users
        WHERE username = %s
    """, (session["user"],))

    user = cur.fetchone()

    cur.close()
    conn.close()

    stats = {
        "orders": len(orders),
        "approved": 0,
        "alerts": 0,
        "blocked_ips": 0,
        "blocked_devices": 0
    }

    return render_template(
        "dashboard.html",
        stats=stats,
        orders=orders,
        columns=columns,
        user=user
    )


# ------------------------
# LOGOUT
# ------------------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
