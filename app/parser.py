# coding: utf-8
import re
import pydantic
import random

from playwright.async_api import async_playwright, Page
from abc import ABC, abstractmethod

import util
import model


def get_parser_by(url: str):

    match = re.search(r"^(?:https?:\/\/)?(?:www\.)?([^\/\?#]+)", url)
    match match.group(1):
        case Fedresurs._domain:
            return Fedresurs
        case _:
            pass


class Site(ABC):

    @abstractmethod
    async def fetch_payload():
        """Метод получения полезных данных с конкретного сайта"""
        pass


class Fedresurs(Site):

    _domain = "fedresurs.ru"

    def __init__(
        self,
        headless: bool,
        user_agent: list | set | tuple = None,
        proxies: list | set | tuple = None,
    ):

        self.headless: bool = headless
        self.user_agent: list | set | tuple = (
            random.choice(user_agent) if user_agent else "Mozilla/5.0"
        )
        self.proxies: list | set | tuple = proxies if proxies else []
        self._results = {}

    @util.retry(5)
    async def fetch_payload(self, data: model.ExcelData) -> model.FedresursData:
        """_summary_

        Args:
            url (str): _description_
            inn (str): _description_

        Returns:
            model.Fedresurs: _description_
        """

        async with async_playwright() as pw:

            try:
                # Конфигурация бразуера
                browser = await pw.chromium.launch(headless=self.headless)
                context = await browser.new_context(
                    user_agent=self.user_agent,
                    proxy={"server": random.choice(self.proxies)},
                )
                # Получаем объект страницы
                page = await context.new_page()

                await self.__search_man(page, data.url, data.inn_number)

                if await self.__main_page_man(page):
                    # Находим нужные данные
                    for target in [
                        ["a", r"^\s.{3,}-\d{3,}/\d{4}\s$", "case_number"],
                        ["a", r"^\s.*\sот\s\d{2}.\d{2}.\d{4}\s$", "last_date"],
                    ]:
                        result = await self.__get_data(page, target[0], target[1])
                        self._results[target[2]] = result if result else ""
                    try:
                        return model.FedresursData(
                            inn_number=data.inn_number, **self._results
                        )
                    except pydantic.ValidationError:
                        pass
            finally:
                await browser.close()

    @util.retry(3)
    async def __search_man(self, page: Page, url: str, inn: str) -> None:
        """Поиск карточки пользователя

        Args:
            page (_type_): Page
            url (str): url
            inn (int): inn
        """
        await page.goto(
            f"{url}entities?searchString={inn}",
            wait_until="networkidle",
            timeout=60000,
        )
        await page.wait_for_selector(f"text={inn}", timeout=10000)

    @util.retry(3)
    async def __main_page_man(self, page: Page) -> bool | None:
        """Открыть карточку пользователя

        Args:
            page (_type_): Page
        """

        # Заходим на страницу банкрота
        locator = await page.wait_for_selector(
            "text=Вся информация", state="visible", timeout=10000
        )
        if locator:
            await locator.scroll_into_view_if_needed()
            await locator.click()
            await page.wait_for_selector(
                "text=Сведения о банкротстве", state="visible", timeout=10000
            )
            return True

    @util.retry(3)
    async def __get_data(self, page: Page, tag: str, text: str) -> str:
        """Получаем данные по определенному локатору, через регулярные варажения
        Args:
            page (Page): _description_
            tag (str): _description_
            text (str): _description_

        Returns:
            _type_: _description_
        """

        # Попытка найти элемент с точным текстом
        locator = page.locator(tag, has_text=re.compile(text)).first
        found = await locator.inner_text(timeout=10000)
        return found
