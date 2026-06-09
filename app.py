from flask import Flask, render_template, request, redirect, session, url_for

app = Flask(__name__)
app.secret_key = "chave_super_secreta"

# usuário fixo (depois pode virar banco de dados)
USER = {
    "username": "admin",
    "password": "123456"
}

# LOGIN
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == USER["username"] and password == USER["password"]:
            session["user"] = username
            return redirect(url_for("dashboard"))

        return render_template("login.html", error="Usuário ou senha inválidos")

    return render_template("login.html")


# DASHBOARD (SEU PAINEL ORIGINAL)
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    stats = {
        "orders": 1248,
        "approved": 1182,
        "alerts": 19,
        "blocked_ips": 47,
        "blocked_devices": 12
    }

    return render_template(
        "dashboard.html",
        stats=stats
    )


# LOGOUT
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
