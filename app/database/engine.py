# -*- coding: utf-8 -*-
from abc import ABC
from sqlalchemy import create_engine, pool
from sqlalchemy.ext.asyncio import create_async_engine

__all__ = ["EnginePSQL", "EngineSQLite"]


class Engine(ABC):

    __name__ == "Engine"

    def __init__(self, **kwargs) -> None:
        for key, value in kwargs.items():
            setattr(self, key, value)
        self._engine = None


class EnginePSQL(Engine):
    """Union all custom sql requests."""

    __name__ = "EnginePSQL"

    def __init__(
        self,
        url: str = None,
        connect_args: dict = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._connect_args = connect_args if connect_args else {}
        self._url = url
        self.__create_engine()

    def __create_engine(self) -> None:

        func = create_async_engine if "asyncpg" in self._url else create_engine
        self._engine = func(
            self._url, connect_args=self._connect_args, poolclass=pool.NullPool
        )


class EngineSQLite(Engine):
    """Union all custom sql requests."""

    __name__ = "EngineSQLite"

    def __init__(
        self,
        url: str,
        connect_args: dict = None,
        **kwargs,
    ):
        super().__init__()
        self.connect_args = connect_args if connect_args else {}
        self.url = url
        self.__create_engine(**kwargs)

    def __create_engine(self, **kwargs) -> None:

        self._engine = create_async_engine(
            self.url,
            connect_args=self.connect_args,
            poolclass=pool.NullPool,
            **kwargs,
        )
