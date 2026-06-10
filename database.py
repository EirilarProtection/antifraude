import psycopg2
import os

def get_connection():
    db_url = os.getenv("DATABASE_URL")

    if not db_url:
        raise Exception("DATABASE_URL não configurada no Railway")

    return psycopg2.connect(db_url, sslmode="require")
