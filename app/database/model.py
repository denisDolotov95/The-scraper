# -*- coding: utf-8 -*-
from datetime import datetime

from sqlalchemy import Sequence, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class INN(Base):

    __tablename__ = "inn"

    __table_args__ = (
        UniqueConstraint("inn_number", "last_date", name="uq_inn_numb_last_date"),
    )
    
    user_id_seq = Sequence("user_id_seq", start=0, increment=1)

    id: Mapped[int] = mapped_column(user_id_seq, primary_key=True)
    inn_number: Mapped[int] = mapped_column(nullable=False)
    case_number: Mapped[str] = mapped_column(nullable=False)
    last_date: Mapped[datetime] = mapped_column(nullable=False)
    # created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    
    

    def __init__(self, inn_number: int, case_number: str, last_date: datetime):

        self.inn_number = inn_number
        self.case_number = case_number
        self.last_date = last_date

    def __repr__(self):

        return (
            f"INN(id={self.id}, inn_number={self.inn_number}, case_number={self.case_number}, last_date={self.last_date})"
        )

    def __str__(self):

        return f"id={self.id}, inn_number={self.inn_number}, case_number={self.case_number}, last_date={self.last_date}"
