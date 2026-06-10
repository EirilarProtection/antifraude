import psycopg2

DATABASE_URL = "postgresql://postgres:OfEYKNGiqqhUOhsNlwuYyxRzrMiiLsIj@acela.proxy.rlwy.net:22734/railway"

def get_connection():
    return psycopg2.connect(
        DATABASE_URL,
        sslmode="require"
    )
