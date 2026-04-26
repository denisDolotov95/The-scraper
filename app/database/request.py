# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from sqlalchemy import Sequence, select, update, delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker, Session

from .engine import Engine, EnginePSQL, EngineSQLite

__all__ = ["_Session"]


class Update(ABC):
    """Define update sql requests."""

    @abstractmethod
    def update_by(self):
        pass

    @abstractmethod
    def upsert_by(self):
        pass


class Delete(ABC):
    """Define delete sql requests."""

    @abstractmethod
    def delete_by(self):
        pass


class Select(ABC):
    """Define select sql requests."""

    @abstractmethod
    def find_by(self):
        pass

    @abstractmethod
    def find_all_by(self):
        pass

    @abstractmethod
    def get_number_sequense(self):
        pass


class Insert(ABC):
    """Define insert sql requests."""

    @abstractmethod
    def add_by(self):
        pass


class Request(Update, Delete, Select, Insert):

    def __init__(self, *args, isolation_level=None, **kwargs):
        self._isolation_level = isolation_level

    @abstractmethod
    def _create_session():
        pass

    def _set_isolation_level(self, s: Session):
        if self._isolation_level:
            s.connection(execution_options={"isolation_level": self._isolation_level})


class Repository(Request):
    """Репозиторий БД, представлен ввиде адаптера к базе данных"""

    def __init__(self, *args, **kwargs):

        self._session = None
        super().__init__(*args, **kwargs)

    def _create_session(self, engine: Engine, **kw) -> None:
        """autoflush: при значении True (значение по умолчанию) будет автоматически
        вызываться метод Session.flush(),
        который записывает все изменения в базу данных
        expire_on_commit – По умолчанию установлено значение True. При True
        все экземпляры будут полностью уничтожены после каждого commit(), так что все
        обращения к атрибутам/объектам после завершенной транзакции будут
        загружаться из самого последнего состояния базы данных
        """
        self._session = sessionmaker(bind=engine._engine, class_=AsyncSession, **kw)

    async def update_by(self, model: object, filter_by: dict, **val):

        async with self._session.begin() as s:
            self._set_isolation_level(s)
            await s.execute(update(model).filter_by(**filter_by).values(**val))

    async def upsert_by(
        self, model: object, index_elements: list, insert_val: dict, update_val: dict
    ):

        async with self._session.begin() as s:
            self._set_isolation_level(s)
            stmt = insert(model).values(**insert_val)
            upsert_stmt = stmt.on_conflict_do_update(
                index_elements=index_elements,  # Column(s) to check for conflict
                set_=dict(**update_val),
            )
            s.execute(upsert_stmt)

    async def delete_by(self, model: object):

        async with self._session.begin() as s:
            self._set_isolation_level(s)
            await s.delete(model)

    async def find_by(self, model: object, **filter_by):

        async with self._session.begin() as s:
            self._set_isolation_level(s)
            result = await s.execute(select(model).filter_by(**filter_by))
            return result.first()

    async def find_all_by(self, model: object, **filter_by):

        async with self._session.begin() as s:
            self._set_isolation_level(s)
            result = await s.execute(select(model).filter_by(**filter_by))
            return result.all()

    async def get_number_sequense(self, **kwargs):

        async with self._session.begin() as s:
            self._set_isolation_level(s)
            return await s.execute(Sequence(**kwargs))

    async def add_by(self, model: object):

        try:
            async with self._session.begin() as s:
                self._set_isolation_level(s)
                s.add(model)
        except IntegrityError:
            pass


class _Session:

    def __init__(self, engine: Engine) -> None:

        self._engine = engine

    def new_session(self, *args, isolation_level: str = None, **kwargs) -> Repository:
        """Получить объект сессии c фикированным набором самописных методов,
        для лаконичности и коротких запросов по принципу CRUD.

        Raises:==
            ValueError: _description_

        Yields:
            Session: _description_
        """
        match self._engine.__name__:
            case EnginePSQL.__name__ | EngineSQLite.__name__:
                repo = Repository(isolation_level=isolation_level)
                repo._create_session(
                    self._engine, *args, expire_on_commit=False, **kwargs
                )
                return repo
            case _:
                raise ValueError("not found engine")
