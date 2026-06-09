from flask import Flask, render_template
import os

app = Flask(__name__)

@app.route("/")
def dashboard():

    stats = {
        "orders": 0,
        "approved": 0,
        "alerts": 0,
        "blocked_ips": 0,
        "blocked_devices": 0
    }

    return render_template(
        "dashboard.html",
        stats=stats
    )

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )
