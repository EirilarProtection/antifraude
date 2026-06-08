import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)

cursor = conn.cursor()

cursor.execute("""
INSERT INTO transactions (customer_name, value, status)
VALUES 
('João Silva', 150.50, 'ok'),
('Maria Souza', 999.90, 'suspeito'),
('Carlos Lima', 49.99, 'ok')
""")

conn.commit()
conn.close()

print("Dados inseridos com sucesso!")
