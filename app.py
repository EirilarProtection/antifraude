from flask import Flask, render_template, request, redirect, session, jsonify
from database import get_conn
import os

app = Flask(__name__)
app.secret_key = "CHANGE_THIS_SECRET"


# -----------------------------
# HOME
# -----------------------------
@app.route("/")
def home():
    if "user_id" in session:
        return redirect("/dashboard")
    return redirect("/login")


# -----------------------------
# REGISTER
# -----------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_conn()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO users (email, password_hash, risk_score, risk_level)
            VALUES (%s, %s, 0, 'LOW')
        """, (email, password))

        conn.commit()

        return redirect("/login")

    return render_template("register.html")


# -----------------------------
# LOGIN
# -----------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_conn()
        cur = conn.cursor()

        cur.execute("""
            SELECT id FROM users
            WHERE email=%s AND password_hash=%s
        """, (email, password))

        user = cur.fetchone()

        if user:
            session["user_id"] = user[0]
            return redirect("/dashboard")

    return render_template("login.html")


# -----------------------------
# DASHBOARD
# -----------------------------
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    return render_template("dashboard.html")


# -----------------------------
# API STATS
# -----------------------------
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


# -----------------------------
# LOGIN HISTORY
# -----------------------------
@app.route("/api/logins")
def logins():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT user_id, ip_address, country, browser, login_date
        FROM login_history
        ORDER BY login_date DESC
        LIMIT 20
    """)

    rows = cur.fetchall()

    return jsonify([
        {
            "user_id": r[0],
            "ip": r[1],
            "country": r[2],
            "browser": r[3],
            "date": str(r[4])
        }
        for r in rows
    ])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
