from flask import Flask, render_template, request, redirect, session, url_for
import os
import psycopg2

app = Flask(__name__)
app.secret_key = "chave_super_secreta"

DATABASE_URL = os.getenv("DATABASE_URL")

# ==========================
# CONEXÃO POSTGRESQL
# ==========================
def get_connection():
    if not DATABASE_URL:
        raise Exception("DATABASE_URL não configurada")

    return psycopg2.connect(
        DATABASE_URL,
        sslmode="require"
    )

# ==========================
# LOGIN
# ==========================
@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        try:

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

            return render_template(
                "login.html",
                error="Usuário ou senha inválidos"
            )

        except Exception as e:
            return f"Erro de banco: {e}"

    return render_template("login.html")

# ==========================
# REGISTRO
# ==========================
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]
        email = request.form["email"]
        phone = request.form["phone"]
        birthdate = request.form["birthdate"]

        try:

            conn = get_connection()
            cur = conn.cursor()

            cur.execute(
                "SELECT id FROM users WHERE username = %s",
                (username,)
            )

            exists = cur.fetchone()

            if exists:

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
                    password,
                    email,
                    phone,
                    birthdate
                )
                VALUES
                (%s,%s,%s,%s,%s)
            """, (
                username,
                password,
                email,
                phone,
                birthdate
            ))

            conn.commit()

            cur.close()
            conn.close()

            return redirect(url_for("login"))

        except Exception as e:
            return f"Erro de banco: {e}"

    return render_template("register.html")

# ==========================
# DASHBOARD
# ==========================
@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect(url_for("login"))

    try:

        conn = get_connection()
        cur = conn.cursor()

        # pedidos
        cur.execute("""
            SELECT *
            FROM orders
            ORDER BY id DESC
            LIMIT 100
        """)

        columns = [desc[0] for desc in cur.description]
        orders = cur.fetchall()

        # usuário logado
        cur.execute("""
            SELECT username, email, phone, birthdate
            FROM users
            WHERE username = %s
        """, (session["user"],))

        user = cur.fetchone()

        # estatísticas reais
        cur.execute("SELECT COUNT(*) FROM orders")
        total_orders = cur.fetchone()[0]

        cur.execute("""
            SELECT COUNT(*)
            FROM orders
            WHERE status = 'Aprovado'
        """)
        approved = cur.fetchone()[0]

        cur.execute("""
            SELECT COUNT(*)
            FROM orders
            WHERE status = 'Suspeito'
        """)
        alerts = cur.fetchone()[0]

        cur.execute("""
            SELECT COUNT(DISTINCT ip)
            FROM orders
        """)
        ips = cur.fetchone()[0]

        cur.execute("""
            SELECT COUNT(DISTINCT device)
            FROM orders
        """)
        devices = cur.fetchone()[0]

        cur.close()
        conn.close()

        stats = {
            "orders": total_orders,
            "approved": approved,
            "alerts": alerts,
            "blocked_ips": ips,
            "blocked_devices": devices
        }

        return render_template(
            "dashboard.html",
            stats=stats,
            user=user,
            orders=orders,
            columns=columns
        )

    except Exception as e:
        return f"Erro de banco: {e}"

# ==========================
# LOGOUT
# ==========================
@app.route("/logout")
def logout():

    session.pop("user", None)

    return redirect(url_for("login"))

# ==========================
# START
# ==========================
if __name__ == "__main__":
    app.run(debug=True)
