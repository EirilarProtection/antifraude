from pathlib import Path

env_content = """DB_HOST=localhost
DB_PORT=5432
DB_NAME=antifraude
DB_USER=postgres
DB_PASSWORD=@324260
"""

Path(".env").write_text(env_content)

print("Arquivo .env criado com sucesso!")
