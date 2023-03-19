import datetime
import decimal
from typing import List

from sqlalchemy import String, SmallInteger, DateTime, Numeric, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.models.base import Base
from src.app.models.order import Order


class Deal(Base):
    __tablename__ = 'deals'

    id: Mapped[int] = mapped_column(primary_key=True)
    pair: Mapped[str] = mapped_column(String(255), nullable=False)
    safety_order_count: Mapped[int] = mapped_column(SmallInteger(), nullable=False, default=0)
    date_open: Mapped[datetime.datetime] = mapped_column(DateTime(), nullable=False)
    date_close: Mapped[datetime.datetime] = mapped_column(DateTime(), nullable=True, default=None)
    pnl: Mapped[decimal] = mapped_column(Numeric(), nullable=True)
    bot_id: Mapped[int] = mapped_column(Integer(), nullable=False)
    order: Mapped[List["Order"]] = relationship(cascade="all, delete", passive_deletes=True)
