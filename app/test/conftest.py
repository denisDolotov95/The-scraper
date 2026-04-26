# coding: utf-8
import os
import pytest

from pathlib import Path

# from sqlalchemy.orm import sessionmaker

from ..database import request, engine, model as sql_model

all = ["db_session"]


@pytest.fixture(scope="session", autouse=True)
def db_engine():
    """Фикстура для создания двигателя к БД.
    Используется локальный файл *.db для тестирования.
    В конце тестирования файл удаляется.

    Yields:
        _type_: EngineSQLite
    """

    DB_PATH = "./app/test/test.db"

    db_file = Path(DB_PATH)
    if not db_file.is_file():
        with open(DB_PATH, "w+"):
            pass

    new_engine = engine.EngineSQLite(f"sqlite:///{DB_PATH}")
    sql_model.Base.metadata.drop_all(new_engine._engine)
    sql_model.Base.metadata.create_all(new_engine._engine)

    new_engine = engine.EngineSQLite(f"sqlite+aiosqlite:///{DB_PATH}")

    yield new_engine

    os.remove(DB_PATH)


@pytest.fixture(scope="function")
def db_session(db_engine):
    """Фикстура для создания сессий к БД,
    используя уже готовую конфигурацию движка

    Yields:
        _type_: Session
    """

    session = request._Session(db_engine)
    yield session.new_session()  # Передаем сессию в тест
