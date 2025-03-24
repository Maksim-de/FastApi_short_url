import os
import asyncio
import asyncpg
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

import os

base_url = os.getenv("BASE_URL", "http://localhost:8000")

# SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
# SMTP_USER = os.getenv("SMTP_USER")

SECRET = os.getenv("SECRET")
# import os, base64
# print(base64.urlsafe_b64encode(os.urandom(32)).decode())


# async def check_asyncpg_connection(host, port, database, user, password):
#     """Проверяет подключение к PostgreSQL базе данных асинхронно."""
#     try:
#         conn = await asyncpg.connect(host=host,
#             port=port,
#             database=database,
#             user=user,
#             password=password, timeout=5)  # Используем параметры
#         print("Успешное асинхронное подключение к PostgreSQL!")
#         await conn.close()
#         return True
#     except asyncpg.PostgresConnectionError as e:
#         print(f"Ошибка асинхронного подключения к PostgreSQL: {e}")
#         return False
#     except Exception as e:
#         print(f"Общая ошибка: {e}")
#         return False


# async def main():
#     """Основная функция для запуска проверки подключения."""
#     if await check_asyncpg_connection(DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS):  # Передаем параметры
#         print("Асинхронное подключение к базе данных работает!")
#     else:
#         print("Проверьте параметры асинхронного подключения!")


# if __name__ == "__main__":
#     asyncio.run(main())