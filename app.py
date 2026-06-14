from flask import Flask, render_template, request, redirect, session, jsonify
from database import get_conn
from datetime import datetime

app = Flask(**name**)
app.secret_key = "CHANGE_THIS_SECRET"

# -----------------------------------

# HOME

# -----------------------------------

@app.route("/")
def home():
if "user_id" in session:
return redirect("/dashboard")
return redirect("/login")

# -----------------------------------

# REGISTER

# -----------------------------------

@app.route("/register", methods=["GET", "POST"])
def register():

```
if request.method == "POST":

    username = request.form["username"]
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    email = request.form["email"]
    birthdate = request.form["birthdate"]
    password = request.form["password"]

    full_name = f"{first_name} {last_name}"

    conn = get_conn()
    cur = conn.cursor()

    try:

        cur.execute(
            """
            SELECT id
            FROM users
            WHERE email=%s OR username=%s
            """,
            (email, username)
        )

        exists = cur.fetchone()

        if exists:
            cur.close()
            conn.close()
            return "Usuário ou e-mail já cadastrado"

        cur.execute(
            """
            INSERT INTO users
            (
                username,
                email,
                full_name,
                birthdate,
                password_hash,
                risk_score,
                risk_level,
                account_status,
                failed_logins,
                login_count,
                created_at
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                0,
                'LOW',
                'ACTIVE',
                0,
                0,
                NOW()
            )
            """,
            (
                username,
                email,
                full_name,
                birthdate,
                password
            )
        )

        conn.commit()

    finally:
        cur.close()
        conn.close()

    return redirect("/login")

return render_template("register.html")
```

# -----------------------------------

# LOGIN

# -----------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

```
if request.method == "POST":

    login_value = request.form["email"]
    password = request.form["password"]

    conn = get_conn()
    cur = conn.cursor()

    try:

        cur.execute(
            """
            SELECT
                id,
                username,
                password_hash,
                failed_logins
            FROM users
            WHERE email=%s
               OR username=%s
            """,
            (login_value, login_value)
        )

        user = cur.fetchone()

        if not user:
            return render_template(
                "login.html",
                error="Usuário não encontrado"
            )

        user_id = user[0]
        username = user[1]
        db_password = user[2]

        if password != db_password:

            cur.execute(
                """
                UPDATE users
                SET failed_logins =
                    COALESCE(failed_logins,0) + 1
                WHERE id=%s
                """,
                (user_id,)
            )

            conn.commit()

            return render_template(
                "login.html",
                error="Senha incorreta"
            )

        cur.execute(
            """
            UPDATE users
            SET
                last_login = NOW(),
                login_count = COALESCE(login_count,0)+1,
                failed_logins = 0
            WHERE id=%s
            """,
            (user_id,)
        )

        cur.execute(
            """
            INSERT INTO login_history
            (
                user_id,
                ip_address,
                city,
                state,
                country,
                browser,
                operating_system,
                login_date
            )
            VALUES
            (
                %s,
                %s,
                '',
                '',
                '',
                %s,
                %s,
                NOW()
            )
            """,
            (
                user_id,
                request.remote_addr,
                request.user_agent.browser or "Unknown",
                request.user_agent.platform or "Unknown"
            )
        )

        conn.commit()

        session["user_id"] = user_id
        session["username"] = username

        return redirect("/dashboard")

    finally:
        cur.close()
        conn.close()

return render_template("login.html")
```

# -----------------------------------

# LOGOUT

# -----------------------------------

@app.route("/logout")
def logout():
session.clear()
return redirect("/login")

# -----------------------------------

# DASHBOARD

# -----------------------------------

@app.route("/dashboard")
def dashboard():

```
if "user_id" not in session:
    return redirect("/login")

return render_template("dashboard.html")
```

# -----------------------------------

# API STATS

# -----------------------------------

@app.route("/api/stats")
def stats():

```
if "user_id" not in session:
    return jsonify({"error": "unauthorized"}), 401

conn = get_conn()
cur = conn.cursor()

try:

    cur.execute("SELECT COUNT(*) FROM users")
    users = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM login_history")
    logins = cur.fetchone()[0]

    cur.execute(
        """
        SELECT COUNT(*)
        FROM users
        WHERE risk_score > 70
        """
    )
    high_risk = cur.fetchone()[0]

    return jsonify(
        {
            "users": users,
            "logins": logins,
            "high_risk": high_risk
        }
    )

finally:
    cur.close()
    conn.close()
```

# -----------------------------------

# API LOGINS

# -----------------------------------

@app.route("/api/logins")
def logins():

```
if "user_id" not in session:
    return jsonify([])

conn = get_conn()
cur = conn.cursor()

try:

    cur.execute(
        """
        SELECT
            user_id,
            ip_address,
            country,
            browser,
            login_date
        FROM login_history
        ORDER BY login_date DESC
        LIMIT 50
        """
    )

    rows = cur.fetchall()

    return jsonify(
        [
            {
                "user_id": r[0],
                "ip": r[1],
                "country": r[2],
                "browser": r[3],
                "date": str(r[4])
            }
            for r in rows
        ]
    )

finally:
    cur.close()
    conn.close()
```

if **name** == "**main**":
app.run(
host="0.0.0.0",
port=8080,
debug=True
)
