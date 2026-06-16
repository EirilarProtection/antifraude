from flask import Flask, render_template, session, redirect
from database import get_conn

app = Flask(__name__)
app.secret_key = "dev_secret_123"


@app.route("/")
def home():
    return redirect("/dashboard")


@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect("/login")

    conn = get_conn()
    cur = conn.cursor()

    # KPIs
    cur.execute("SELECT COUNT(*) FROM users")
    users_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM orders")
    orders_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM fraud_events")
    fraud_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM notifications")
    alerts_count = cur.fetchone()[0]

    # Últimos pedidos
    cur.execute("""
        SELECT id, user_id, total_amount, status
        FROM orders
        ORDER BY id DESC
        LIMIT 10
    """)
    orders = cur.fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        users_count=users_count,
        orders_count=orders_count,
        fraud_count=fraud_count,
        alerts_count=alerts_count,
        orders=orders
    )


if __name__ == "__main__":
    app.run(debug=True)
