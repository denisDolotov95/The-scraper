# coding: utf-8
import os
import pandas as pd
import asyncio
import logging
import logging.handlers as l_handl

import util
import parser as pars
import config as cfg
import model

from database import model as sql_model

logger = logging.getLogger(__name__)

for log in (logging.getLogger(n) for n in logging.root.manager.loggerDict):
    if "1" == os.getenv("DEBUG", "0"):
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)

rot_file_handler = l_handl.RotatingFileHandler(
    "./app/logs/app.log", maxBytes=50 * 1024 * 1024, backupCount=10, encoding="utf-8"
)

logging.basicConfig(
    handlers=None if "1" == os.getenv("LOG_STDOUT", "0") else [rot_file_handler],
    format=(
        "[%(asctime)s] (%(filename)s:%(lineno)d %(threadName)s) "
        '%(levelname)s - %(name)s: "%(message)s"'
    ),
)


@util.semaphore(cfg.sem)
async def runner(data: pd.Series, pars: pars.Fedresurs | pars.KadArbitr):
    """Запуск ранера, который будет инициализировать подключение через бразуер
    и получать исходные данные, если данные получены и они непустые (получены все данные),
    то сохраняем их в БД.

    Args:
        data (pd.Series): строка с данными из *.csv
    """

    logger.info(f"Начинается поиск по: \n{data.to_string()}")

    result = await pars.fetch_payload(model.ExcelData(**data.to_dict()))
    logger.info(f"Получены данные {result} по: \n{data.to_string()}")

    if result:
        logger.info(f"Сохранить данные {result} в базу")
        req = cfg.sql_req.new_session()
        await req.add_by(pars._orm(**result.model_dump()))


async def main():

    df = pd.read_csv(
        cfg.INN_FILE,
        dtype={"url": "string", "inn_number": "string", "case_number": "string"},
    )

    logger.info(f"\nПолучено: \n{df.head(100)}")
    tasks = list()
    # Создаем задачи
    async for raw in util.async_generator(df):
        type_pars = pars.get_parser_by(raw["url"])
        if type_pars:
            p = type_pars(
                headless=cfg.HEADLESS, user_agent=cfg.USER_AGENTS, proxies=cfg.PROXIES
            )
            tasks.append(runner(raw, p))
    # Добавляем задачи в цикл событий
    await asyncio.gather(*tasks)
    logger.info("Поиск закончен")


asyncio.run(main())
