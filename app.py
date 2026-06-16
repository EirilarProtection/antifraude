from flask import Flask, render_template, request, redirect, session
from database import get_conn

app = Flask(__name__)
app.secret_key = "dev_secret_123"

# =========================
# LOGIN
# =========================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE email=%s AND password=%s", (email, password))
        user = cur.fetchone()

        if user:
            session["user_id"] = user[0]
            return redirect("/dashboard")

    return render_template("login.html")


# =========================
# REGISTER
# =========================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_conn()
        cur = conn.cursor()
        cur.execute("INSERT INTO users(email, password) VALUES(%s,%s)", (email, password))
        conn.commit()

        return redirect("/login")

    return render_template("register.html")


# =========================
# DASHBOARD
# =========================
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM users")
    users = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM orders")
    orders = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM fraud_events")
    frauds = cur.fetchone()[0]

    return render_template("dashboard.html",
        users=users,
        orders=orders,
        frauds=frauds
    )


# =========================
# LOGOUT
# =========================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)
