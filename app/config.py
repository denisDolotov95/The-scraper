# coding: utf-8
import os

from database import engine, request
#(
#            f"{self._driver}{'+asyncpg' if self._async_req else ''}://{self._username}:"
#            + f"{self._password}@{self._host}:"
#            + f"{self._port}/{self._service_name}"
#        )
# f"sqlite+aiosqlite:///{file_path}"
engine = engine.EnginePSQL(
    url=os.getenv(
        "DB_URL",
        os.path.join("database", "database.db"),
    )
)
sql_req = request._Session(engine)

# Для усановки семафора на конкретную функцию
MAX_CONCURRENCY = int(os.environ.get("MAX_CONCURRENCY", 4))

# Сколько ретраев необходимо для повторного подключения
MAX_RETRIES = int(os.environ.get("MAX_RETRIES", 5))

# Начальное значение для задержки (используется экспоненциальное)
BASE_BACKOFF = float(os.environ.get("BASE_BACKOFF", 1))

# Добавим разные агенты, для обхода блокировки
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
]

# Добавим разные прокси, для обхода блокировки
PROXIES = [
    None,  # без прокси
    "http://user:pass@1.2.3.4:3128",
    # "http://...": добавить если есть
]

# BLOCK_RESOURCE_TYPES = {"image", "media", "font", "stylesheet"}

