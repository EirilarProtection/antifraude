import psycopg2

def get_connection():
    return psycopg2.connect(
        "postgresql://postgres:OfEYKNGiqqhUOhsNlwuYyxRzrMiiLsIj@acela.proxy.rlwy.net:22734/railway"
    )
