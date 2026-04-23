# coding: utf-8
import asyncio
import logging

from functools import wraps

from config import MAX_CONCURRENCY, BASE_BACKOFF, MAX_RETRIES


def retry(
    max_tries: int = MAX_RETRIES,
    delay: int = BASE_BACKOFF,
    exceptions: tuple = (TimeoutError, RuntimeError),
):
    """Декоратор для повторного вызова доменной модели при возникновении ошибок"""

    def decorator(func):
        @wraps(func)  # Сохраняет метаданные оригинальной функции (__name__, __doc__)
        async def wrapper(*args, **kwargs):
            tries = 0
            for attempt in range(1, max_tries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    tries += 1
                    if tries == max_tries:
                        logging.error(
                            f"{func.__name__} закончился неудачей после {MAX_RETRIES} попыток"
                        )
                        raise e
                    new_delay = delay * (2 ** (attempt - 1))
                    logging.warning(
                        f"{func.__name__} попытка {attempt}; искючение: {e}; задержка {new_delay}"
                    )
                    await asyncio.sleep(new_delay)
                except Exception as e:
                    logging.error(f"{func.__name__} необработанное исключение: {e}")

        return wrapper

    return decorator


def semaphore(max_tasks: int = MAX_CONCURRENCY):
    """Декоратор для ограничения количество доступов к какой-либо доменной модели

    Args:
        max_concurrent_tasks (_type_): сколько раз можно вызвать
    """
    # Создаем семафор для ограничения доступа какой-либо доменной модели
    sem = asyncio.Semaphore(max_tasks)

    def decorator(func):
        @wraps(func)  # Сохраняет метаданные оригинальной функции (__name__, __doc__)
        async def wrapper(*args, **kwargs):
            # Захватываем семафор перед выполнением функции
            with sem:
                return await func(*args, **kwargs)

        return wrapper

    return decorator
