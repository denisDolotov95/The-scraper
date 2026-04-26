# coding: utf-8
import pandas as pd
import asyncio
import logging

from functools import wraps
from playwright.async_api import TimeoutError

from config import BASE_BACKOFF, MAX_RETRIES


async def async_generator(df: pd.DataFrame):
    for i, raw in df.iterrows():
        # await asyncio.sleep(1)
        yield raw
        df.drop(i)


def retry(
    max_tries: int = MAX_RETRIES,
    delay: int = BASE_BACKOFF,
    exceptions: tuple = (TimeoutError,),
):
    """Декоратор для повторного вызова доменной модели при возникновении ошибок"""

    def decorator(func):
        @wraps(func)  # Сохраняет метаданные оригинальной функции (__name__, __doc__)
        async def wrapper(*args, **kwargs):
            tries = 0
            for attempt in range(1, max_tries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    tries += 1
                    if tries == max_tries:
                        logging.error(
                            f"{func.__name__}({args}, {kwargs}) закончился неудачей после {max_tries} попыток"
                        )
                    new_delay = delay * (2 ** (attempt - 1))
                    logging.warning(
                        f"{func.__name__}({args}, {kwargs}) попытка {attempt}; задержка {new_delay};\n{e}"
                    )
                    await asyncio.sleep(new_delay)
                except Exception as e:
                    logging.error(
                        f"{func.__name__}({args}, {kwargs}), необработанное исключение:\n{e}"
                    )

        return wrapper

    return decorator


def semaphore(sem: asyncio.Semaphore):
    """Декоратор для ограничения количество доступов к какой-либо доменной модели

    Args:
        max_concurrent_tasks (_type_): сколько раз можно вызвать
    """

    def decorator(func):
        @wraps(func)  # Сохраняет метаданные оригинальной функции (__name__, __doc__)
        async def wrapper(*args, **kwargs):
            # Захватываем семафор перед выполнением функции
            async with sem:
                return await func(*args, **kwargs)

        return wrapper

    return decorator
