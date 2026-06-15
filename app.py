from flask import Flask, render_template, request, redirect, session, jsonify
from database import *

import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev_secret")

# =========================
# HOME
# =========================
@app.route("/")
def home():
    if "user_id" in session:
        return redirect("/dashboard")
    return redirect("/login")

# =========================
# LOGIN (simples)
# =========================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session["user_id"] = 1
        return redirect("/dashboard")
    return render_template("login.html")

# =========================
# REGISTER
# =========================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        return redirect("/login")
    return render_template("register.html")

# =========================
# LOGOUT
# =========================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# =========================
# DASHBOARD PAGE
# =========================
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

# =========================
# API DASHBOARD STATS
# =========================
@app.route("/api/dashboard")
def api_dashboard():
    return jsonify(get_dashboard_stats())

# =========================
# USERS
# =========================
@app.route("/api/users")
def api_users():
    return jsonify(get_users())

# =========================
# ORDERS (usa login_history se não existir orders)
# =========================
@app.route("/api/orders")
def api_orders():
    return jsonify(get_orders())

# =========================
# FRAUD EVENTS
# =========================
@app.route("/api/fraud-events")
def api_fraud_events():
    return jsonify(get_fraud_events())

# =========================
# ALERTS
# =========================
@app.route("/api/alerts")
def api_alerts():
    return jsonify(get_alerts())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
