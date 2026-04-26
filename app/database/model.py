# -*- coding: utf-8 -*-
from datetime import date

from sqlalchemy import Sequence, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Fedresurs(Base):

    __tablename__ = "fedresurs"

    __table_args__ = (
        UniqueConstraint("inn_number", "last_date", name="uq_inn_numb_last_date"),
    )

    inn_id_seq = Sequence("inn_id_seq", start=0, increment=1)

    # id: Mapped[int] = mapped_column(
    #     inn_id_seq, server_default=inn_id_seq.next_value(), primary_key=True
    # )
    id: Mapped[int] = mapped_column(inn_id_seq, primary_key=True)
    inn_number: Mapped[str] = mapped_column(nullable=False)
    case_number: Mapped[str] = mapped_column(nullable=False)
    last_date: Mapped[date] = mapped_column(nullable=False)
    # created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    def __init__(
        self,
        inn_number: str,
        case_number: str,
        last_date: date,
    ):

        self.inn_number = inn_number
        self.case_number = case_number
        self.last_date = last_date

    def __repr__(self):

        return f"Fedresurs(id={self.id}, inn_number={self.inn_number}, case_number={self.case_number}, last_date={self.last_date})"

    def __str__(self):

        return f"id={self.id}, inn_number={self.inn_number}, case_number={self.case_number}, last_date={self.last_date}"


class KadArbitr(Base):

    __tablename__ = "kadarbitr"

    __table_args__ = (
        UniqueConstraint(
            "case_number",
            "last_date",
            "name_document",
            name="uq_case_numer_last_date_name_document",
        ),
    )

    kadarbitr_id_seq = Sequence("kadarbitr_id_seq", start=0, increment=1)

    # id: Mapped[int] = mapped_column(
    #     inn_id_seq, server_default=inn_id_seq.next_value(), primary_key=True
    # )
    id: Mapped[int] = mapped_column(kadarbitr_id_seq, primary_key=True)
    case_number: Mapped[str] = mapped_column(nullable=False)
    last_date: Mapped[date] = mapped_column(nullable=False)
    name_document: Mapped[str] = mapped_column(nullable=False)
    # created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    def __init__(
        self,
        case_number: str,
        last_date: date,
        name_document: str,
    ):

        self.case_number = case_number
        self.last_date = last_date
        self.name_document = name_document

    def __repr__(self):

        return f"KadArbitr(id={self.id}, case_number={self.case_number}, last_date={self.last_date}, name_document={self.name_document})"

    def __str__(self):

        return f"id={self.id}, case_number={self.case_number}, last_date={self.last_date}, name_document={self.name_document}"
