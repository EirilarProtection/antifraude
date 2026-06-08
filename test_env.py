from dotenv import load_dotenv
import os

load_dotenv()

print("HOST:", os.getenv("DB_HOST"))
print("USER:", os.getenv("DB_USER"))
print("DB:", os.getenv("DB_NAME"))
