# coding: utf-8
import re
import pydantic
import random

from playwright.async_api import async_playwright, Page, TimeoutError
from playwright_stealth import Stealth
from abc import ABC, abstractmethod

import util
import model

from database import model as sql_model


def get_parser_by(url: str):

    match = re.search(r"^(?:https?:\/\/)?(?:www\.)?([^\/\?#]+)", url)
    match match.group(1):
        case Fedresurs._domain:
            return Fedresurs
        case KadArbitr._domain:
            return KadArbitr
        case _:
            pass


class Site(ABC):

    @abstractmethod
    async def fetch_payload(data: model.ExcelData):
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
        self.user_agent: list | set | tuple = user_agent
        self.proxies: list | set | tuple = proxies
        self._orm = sql_model.Fedresurs
        self._results = {}

    @util.retry(5)
    async def fetch_payload(self, data: model.ExcelData) -> model.FedresursData:
        """Получить необходимые данные с сайта

        Args:
            data (model.ExcelData): _description_

        Returns:
            model.FedresursData: _description_
        """

        async with async_playwright() as pw:

            try:
                # Конфигурация бразуера
                browser = await pw.chromium.launch(headless=self.headless)
                context = await browser.new_context(
                    user_agent=(
                        random.choice(self.user_agent)
                        if self.user_agent
                        else "Mozilla/5.0"
                    ),
                    proxy=(
                        {"server": random.choice(self.proxies)}
                        if self.proxies
                        else None
                    ),
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
            # await locator.scroll_into_view_if_needed()
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


class KadArbitr(Site):

    _domain = "kad.arbitr.ru"

    def __init__(
        self,
        headless: bool,
        user_agent: list | set | tuple = None,
        proxies: list | set | tuple = None,
    ):

        self.headless: bool = headless
        self.user_agent: list | set | tuple = user_agent
        self.proxies: list | set | tuple = proxies
        self._orm = sql_model.KadArbitr
        self._results = {}

    @util.retry(5)
    async def fetch_payload(self, data: model.ExcelData) -> model.KadArbitrData:
        """Получить необходимые данные с сайта

        Args:
            data (model.ExcelData): _description_

        Returns:
            model.KadArbitrData: _description_
        """

        async with async_playwright() as pw:

            try:
                # Конфигурация бразуера
                browser = await pw.chromium.launch(headless=self.headless)
                context = await browser.new_context(
                    user_agent=(
                        random.choice(self.user_agent)
                        if self.user_agent
                        else "Mozilla/5.0"
                    ),
                    proxy=(
                        {"server": random.choice(self.proxies)}
                        if self.proxies
                        else None
                    ),
                )
                # Получаем объект страницы
                page = await context.new_page()

                await Stealth().apply_stealth_async(page)

                await page.goto(
                    f"https://kad.arbitr.ru/",
                    wait_until="networkidle",
                    timeout=60000,
                )

                await page.keyboard.press("Escape")

                # Находим банкрота
                await self.__search_man(page, data.case_number)
                await self.__main_page_man(page, data.case_number)

                try:
                    result = await self.__get_data(page)
                    if result:
                        return model.KadArbitrData(
                            case_number=data.case_number,
                            name_document=result[0],
                            last_date=result[1],
                        )
                except pydantic.ValidationError:
                    pass
            finally:
                await browser.close()

    @util.retry(3)
    async def __search_man(self, page: Page, case_number: str) -> None:
        """Поиск карточки пользователя

        Args:
            page (_type_): Page
            case_number (str): case_number
        """
        await page.fill('input[placeholder="например, А50-5568/08"]', case_number)
        # await page.screenshot(path="full_page.png", full_page=True)
        button = page.locator(".b-button-container button", has_text="Найти")  # Точно
        # await button.click()
        await button.scroll_into_view_if_needed()
        box = await button.bounding_box()
        if box:
            # Двигаем мышь в центр кнопки и кликаем
            await page.mouse.click(box["x"] + box["width"] / 4, box["y"] + box["height"] / 2)

    @util.retry(3)
    async def __main_page_man(self, page: Page, case_number: str) -> None:
        """Открыть карточку пользователя

        Args:
            page (_type_): Page
        """

        case = page.locator(".b-container a", has_text=case_number)
        await case.click()
        url = await case.get_attribute("href")
        await page.goto(url, wait_until="domcontentloaded")

    @util.retry(3)
    async def __get_data(self, page: Page) -> tuple[str, str] | None:
        """Получаем данные по определенному локатору
        Args:
            page (Page): _description_

        Returns:
            _type_: _description_
        """

        # Попытка найти элемент с точным текстом
        # Ждем появления контейнера с документами (хронологии)
        try:
            await page.wait_for_selector(".b-case-result", timeout=10000)
        except TimeoutError:
            return

        # Собираем все названия документов
        title_block = page.locator(".b-case-result a")
        name_document = await title_block.first.inner_text()
        parent = title_block.locator("..").locator("..").locator("..")
        # children = await parent.all()
        # for child in children:
        #     print(await child.inner_text()) # Вывод текста каждого ребенка
        last_date = await parent.locator(".b-reg-date").first.inner_text()

        return name_document, last_date
