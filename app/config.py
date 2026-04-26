# coding: utf-8
import os
import asyncio

from database import engine, request

engine = engine.EnginePSQL(
    url=os.getenv(
        "DB_URL",
        "postgresql+asyncpg://postgres:postgres@192.168.0.101:5432/parser",
    )
)
sql_req = request._Session(engine)

# Создаем семафор для ограничения доступа какой-либо доменной модели
MAX_CONCURRENCY = int(os.environ.get("MAX_CONCURRENCY", 20))
sem = asyncio.Semaphore(MAX_CONCURRENCY)

# Сколько ретраев необходимо для повторного подключения
MAX_RETRIES = int(os.environ.get("MAX_RETRIES", 5))

# Начальное значение для задержки (используется экспоненциальное)
BASE_BACKOFF = float(os.environ.get("BASE_BACKOFF", 1))

# Headless mode (безголовый режим) — это работа браузера без графического интерфейса (окна, вкладок, кнопок).
HEADLESS = True

# Имя файла ИНН
INN_FILE = os.environ.get("FILE_INN", "inn.csv")

# Добавим разные агенты, для обхода блокировки
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 YaBrowser/24.x.x.x Safari/537.36",
]

# Добавим разные прокси, для обхода блокировки
# PROXIES = ["socks5://184.178.172.18:15280",
#            "socks5://98.181.137.83:4145"]
PROXIES = ["socks5://5.255.103.55:1080",
           "socks5://109.71.241.67:1080"]
