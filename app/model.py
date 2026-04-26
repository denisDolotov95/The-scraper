# coding: utf-8
import pydantic

from typing import Optional
from datetime import datetime, date


class Base(pydantic.BaseModel):
    pass


class ExcelData(Base):

    url: str
    inn_number: Optional[str]
    case_number: Optional[str | float]


class FedresursData(Base):

    inn_number: str
    case_number: str
    last_date: date | str

    @pydantic.field_validator("last_date")
    @classmethod
    def check_last_date(cls, last_date: str) -> date:

        return datetime.date(datetime.strptime(last_date.split(" от ")[-1], "%d.%m.%Y"))
    
    
class KadArbitrData(Base):

    name_document: str
    case_number: str
    last_date: date | str

    @pydantic.field_validator("last_date")
    @classmethod
    def check_last_date(cls, last_date: str) -> date:

        return datetime.date(datetime.strptime(last_date.split(" от ")[-1], "%d.%m.%Y"))
