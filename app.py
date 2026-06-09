from flask import Flask, render_template, request, redirect, session, url_for
import os
import psycopg2

DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    if not DATABASE_URL:
        raise Exception("DATABASE_URL não configurada no ambiente")

    return psycopg2.connect(
        DATABASE_URL,
        sslmode='require'
    )

app = Flask(__name__)
app.secret_key = "chave_super_secreta"

# "banco de dados" em memória (agora com mais dados)
USERS = {
    "admin": {
        "password": "123456",
        "email": "",
        "phone": "",
        "birthdate": ""
    }
}

# LOGIN
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in USERS and USERS[username]["password"] == password:
            session["user"] = username
            return redirect(url_for("dashboard"))

        return render_template("login.html", error="Usuário ou senha inválidos")

    return render_template("login.html")


# REGISTER
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # novos campos do formulário
        email = request.form["email"]
        phone = request.form["phone"]
        birthdate = request.form["birthdate"]

        if username in USERS:
            return render_template("register.html", error="Usuário já existe")

        USERS[username] = {
            "password": password,
            "email": email,
            "phone": phone,
            "birthdate": birthdate
        }

        return redirect(url_for("login"))

    return render_template("register.html")


# DASHBOARD (PROTEGIDO)
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    user = USERS.get(session["user"])

    stats = {
        "orders": 1248,
        "approved": 1182,
        "alerts": 19,
        "blocked_ips": 47,
        "blocked_devices": 12
    }

    return render_template(
        "dashboard.html",
        stats=stats,
        user=user
    )


# LOGOUT
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
