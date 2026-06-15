from flask import Flask, render_template, request, redirect, session, jsonify
from database import (
    get_conn,
    get_users,
    get_user,
    get_orders,
    get_fraud_events,
    get_fraud_rules,
    get_alerts,
    get_notifications,
    get_login_history,
    get_devices,
    get_geo_tracking,
    get_blacklist,
    get_audit_logs,
    get_active_sessions,
    get_reports,
    get_settings,
    get_dashboard_stats
)
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "eirilar_secret")

@app.route("/")
def home():
    if "user_id" in session:
        return redirect("/dashboard")
    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        return redirect("/dashboard")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        return redirect("/login")
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/api/dashboard")
def api_dashboard():
    return jsonify(get_dashboard_stats())

@app.route("/api/users")
def api_users():
    return jsonify(get_users())

@app.route("/api/orders")
def api_orders():
    return jsonify(get_orders())

@app.route("/api/fraud-events")
def api_fraud_events():
    return jsonify(get_fraud_events())

@app.route("/api/fraud-rules")
def api_fraud_rules():
    return jsonify(get_fraud_rules())

@app.route("/api/alerts")
def api_alerts():
    return jsonify(get_alerts())

@app.route("/api/notifications")
def api_notifications():
    return jsonify(get_notifications())

@app.route("/api/login-history")
def api_login_history():
    return jsonify(get_login_history())

@app.route("/api/devices")
def api_devices():
    return jsonify(get_devices())

@app.route("/api/geo-tracking")
def api_geo_tracking():
    return jsonify(get_geo_tracking())

@app.route("/api/blacklist")
def api_blacklist():
    return jsonify(get_blacklist())

@app.route("/api/audit-logs")
def api_audit_logs():
    return jsonify(get_audit_logs())

@app.route("/api/active-sessions")
def api_active_sessions():
    return jsonify(get_active_sessions())

@app.route("/api/reports")
def api_reports():
    return jsonify(get_reports())

@app.route("/api/settings")
def api_settings():
    return jsonify(get_settings())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
