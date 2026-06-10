import psycopg2
import os

def get_connection():
    db_url = os.getenv("postgresql://postgres:OfEYKNGiqqhUOhsNlwuYyxRzrMiiLsIj@acela.proxy.rlwy.net:22734/railway")

    if not db_url:
        raise Exception("DATABASE_URL não configurada")

    return psycopg2.connect(
        db_url,
        sslmode="require",
        connect_timeout=10
    )
