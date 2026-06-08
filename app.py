from flask import Flask, render_template
import psycopg2
from dotenv import load_dotenv
import os

app = Flask(__name__)
load_dotenv()

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

@app.route("/")
def dashboard():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM transactions ORDER BY id DESC")
    data = cursor.fetchall()

    conn.close()

    return render_template("index.html", data=data)

if __name__ == "__main__":
    app.run(debug=True)
