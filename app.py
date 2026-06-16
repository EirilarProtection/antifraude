from flask import Flask, render_template, request, redirect, session
from database import get_conn

app = Flask(__name__)
app.secret_key = "dev_secret_123"

# ==================================================
# HOME
# ==================================================
@app.route("/")
def home():
    if "user_id" in session:
        return redirect("/dashboard")
    return redirect("/login")


# ==================================================
# LOGIN (simples)
# ==================================================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_conn()
        cur = conn.cursor()

        cur.execute("""
            SELECT id, email 
            FROM users 
            WHERE email=%s AND password=%s
        """, (email, password))

        user = cur.fetchone()
        cur.close()
        conn.close()

        if user:
            session["user_id"] = user[0]
            session["email"] = user[1]
            return redirect("/dashboard")

        return "Login inválido"

    return render_template("login.html")


# ==================================================
# LOGOUT
# ==================================================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ==================================================
# DASHBOARD
# ==================================================
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    conn = get_conn()
    cur = conn.cursor()

    # =========================
    # CARDS (KPIs)
    # =========================

    cur.execute("SELECT COUNT(*) FROM users")
    users = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM orders")
    orders = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM fraud_events")
    frauds = cur.fetchone()[0]

    # =========================
    # LISTA DE USUÁRIOS
    # =========================
    cur.execute("""
        SELECT id, email, status
        FROM users
        ORDER BY id DESC
        LIMIT 50
    """)
    users_list = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "dashboard.html",
        users=users,
        orders=orders,
        frauds=frauds,
        users_list=users_list
    )


# ==================================================
# AÇÕES (exemplo simples)
# ==================================================
@app.route("/block_user/<int:user_id>")
def block_user(user_id):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        UPDATE users
        SET status='blocked'
        WHERE id=%s
    """, (user_id,))

    conn.commit()
    cur.close()
    conn.close()

    return redirect("/dashboard")


@app.route("/unblock_user/<int:user_id>")
def unblock_user(user_id):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        UPDATE users
        SET status='active'
        WHERE id=%s
    """, (user_id,))

    conn.commit()
    cur.close()
    conn.close()

    return redirect("/dashboard")


# ==================================================
# RUN
# ==================================================
if __name__ == "__main__":
    app.run(debug=True)
