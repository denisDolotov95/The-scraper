# -*- coding: utf-8 -*-
from datetime import datetime

from sqlalchemy import Sequence
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# from werkzeug.security import check_password_hash, generate_password_hash


class Base(DeclarativeBase):
    pass
    # metadata = MetaData(schema=os.environ.get("DB_SCHEMA", "prod"))


class INN(Base):

    __tablename__ = "inn"

    # __table_args__ = {"schema": "prod"}
    
    user_id_seq = Sequence("user_id_seq", start=0, increment=1)

    id: Mapped[int] = mapped_column(user_id_seq, primary_key=True)
    inn: Mapped[int] = mapped_column(nullable=False)
    case_number: Mapped[str] = mapped_column(nullable=False)
    last_date: Mapped[datetime] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    def __init__(self, inn: int, case_number: str, last_date: datetime):

        self.inn = inn
        self.case_number = case_number
        self.last_date = last_date

    def __repr__(self):

        return (
            f"INN(id={self.id}, inn={self.inn}, created_at={self.created_at})"
        )

    def __str__(self):

        return f"id={self.id}, inn={self.inn}, created_at={self.created_at}"
