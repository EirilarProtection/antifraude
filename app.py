from flask import Flask, render_template
import os

app = Flask(__name__)

@app.route("/")
def dashboard():

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

if __name__ == "__main__":
    app.run(debug=True)
