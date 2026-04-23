# coding: utf-8
import os
import asyncio
import logging
import logging.handlers as l_handl

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

for log in (logging.getLogger(n) for n in logging.root.manager.loggerDict):
    if "1" == os.getenv("DEBUG", "0"):
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)

rot_file_handler = l_handl.RotatingFileHandler(
    "app.log", maxBytes=50 * 1024 * 1024, backupCount=10, encoding="utf-8"
)

logging.basicConfig(
    handlers=[rot_file_handler],
    format=(
        "[%(asctime)s] (%(filename)s:%(lineno)d %(threadName)s) "
        '%(levelname)s - %(name)s: "%(message)s"'
    ),
)


async def main():

    while True:
        await asyncio.sleep(10000)


asyncio.run(main())
