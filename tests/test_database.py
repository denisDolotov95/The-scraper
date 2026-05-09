# coding: utf-8
from datetime import datetime

import pytest

from src.database import model as sql_model
from src.database import request


class TestDB:
    """Тестирование DML опраций"""

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "temp_data",
        [
            {
                "id": 1,
                "inn_number": '231138771115',
                "case_number": "А32-28873/2024",
                "last_date": datetime.strptime("03.10.2025 00:00:00", "%d.%m.%Y %H:%M:%S"),
            },
            {
                "id": 2,
                "inn_number": '231138771215',
                "case_number": "А32-28873/2024",
                "last_date": datetime.strptime("03.10.2025 00:00:00", "%d.%m.%Y %H:%M:%S"),
            },
        ],
    )
    async def test_add_inn(self, db_session: request._Session, temp_data):
        """Тестирование добавления новгого ИНН

        Args:
            db_session (_Session): экземлеяр сессии
            temp_data (_type_): данные для проверки
        """

        new_inn = sql_model.Fedresurs(
            inn_number=temp_data["inn_number"],
            case_number=temp_data["case_number"],
            last_date=temp_data["last_date"].date(),
        )
        await db_session.add_by(new_inn)

        # inn = await req.find_by(sql_model.Fedresurs, inn_number=temp_data["inn_number"])
        inn = await db_session.find_by(
            sql_model.Fedresurs, inn_number=temp_data["inn_number"]
        )
        print(inn)
        assert inn[0].id == temp_data["id"]
        assert inn[0].inn_number == temp_data["inn_number"]
        assert inn[0].case_number == temp_data["case_number"]
        assert inn[0].last_date == temp_data["last_date"].date()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "temp_data",
        [
            {
                "id": 1,
                "inn_number": '231138771115',
                "case_number": "А32-28873/2024",
                "last_date": datetime.strptime("03.10.2025 00:00:00", "%d.%m.%Y %H:%M:%S"),
            }
        ],
    )
    async def test_add_exist_inn(self, db_session: request._Session, temp_data):
        """Тестирование добавления уже существующего ИНН (сробатывание уникального
        ограничения)

        Args:
            db_session (_Session): экземлеяр сессии
            temp_data (_type_): данные для проверки
        """

        new_inn = sql_model.Fedresurs(
            inn_number=temp_data["inn_number"],
            case_number=temp_data["case_number"],
            last_date=temp_data["last_date"].date(),
        )

        # Дублируем добавление записи в БД
        await db_session.add_by(new_inn)
        await db_session.add_by(new_inn)

        inn = await db_session.find_by(
            sql_model.Fedresurs,
            inn_number=temp_data["inn_number"],
            last_date=temp_data["last_date"].date(),
        )
        assert len(inn) == 1

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "temp_data",
        [
            {
                "id": 1,
                "inn_number": '231138771115',
                "case_number": "А32-28873/2024",
                "last_date": datetime.strptime("03.10.2025 00:00:00", "%d.%m.%Y %H:%M:%S"),
            }
        ],
    )
    async def test_del_exist_inn(self, db_session: request._Session, temp_data):
        """Тестирование удаления уже существующего ИНН (сробатывание уникального
        ограничения)

        Args:
            db_session (_Session): экземлеяр сессии
            temp_data (_type_): данные для проверки
        """

        # Ищем запись в БД и удаляем её
        inn = await db_session.find_by(
            sql_model.Fedresurs,
            inn_number=temp_data["inn_number"],
        )
        await db_session.delete_by(inn[0])
        all_inn = await db_session.find_all_by(
            sql_model.Fedresurs,
        )
        assert len(all_inn) == 1

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "temp_data",
        [
            {
                "id": 1,
                "inn_number": '231138731115',
                "case_number": "А32-28873/2024",
                "last_date": datetime.strptime("03.10.2025 00:00:00", "%d.%m.%Y %H:%M:%S"),
            }
        ],
    )
    async def test_del_not_exist_inn(self, db_session: request._Session, temp_data):
        """Тестирование удаления несуществующего ИНН (сробатывание уникального
        ограничения)

        Args:
            db_session (_Session): экземлеяр сессии
            temp_data (_type_): данные для проверки
        """

        # Ищем запись в БД и удаляем её
        inn = await db_session.find_by(
            sql_model.Fedresurs,
            inn_number=temp_data["inn_number"],
        )
        assert inn == None

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "temp_data",
        [
            {
                "id": 2,
                "inn_number": '231138771215',
                "case_number": "А32-28873/2024",
                "last_date": datetime.strptime("03.10.2025 00:00:00", "%d.%m.%Y %H:%M:%S"),
            }
        ],
    )
    async def test_find_exist_inn(self, db_session: request._Session, temp_data):
        """Тестирование поиска уже существующего ИНН

        Args:
            db_session (_Session): экземлеяр сессии
            temp_data (_type_): данные для проверки
        """

        # Ищем запись в БД
        inn = await db_session.find_by(
            sql_model.Fedresurs,
            inn_number=temp_data["inn_number"],
        )

        assert len(inn) == 1
        assert inn[0].id == temp_data["id"]
        assert inn[0].inn_number == temp_data["inn_number"]
        assert inn[0].case_number == temp_data["case_number"]
        assert inn[0].last_date == temp_data["last_date"].date()

    @pytest.mark.asyncio
    async def test_find_all_inn(self, db_session: request._Session):
        """Тестирование поиска всех ИНН
        Args:
            db_session (_Session): экземлеяр сессии
            temp_data (_type_): данные для проверки
        """

        # Ищем все записи в БД
        all_inn = await db_session.find_all_by(sql_model.Fedresurs)

        assert len(all_inn) == 1
