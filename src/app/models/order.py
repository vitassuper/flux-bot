import decimal
from datetime import datetime

from sqlalchemy import ForeignKey, String, Numeric, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from src.app.models.base import Base


class Order(Base):
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(primary_key=True)
    deal_id: Mapped[int] = mapped_column(ForeignKey('deals.id', ondelete='CASCADE'))
    side: Mapped[str] = mapped_column(String(10), nullable=False)
    price: Mapped[decimal] = mapped_column(Numeric(precision=20, scale=10), nullable=False)
    volume: Mapped[decimal] = mapped_column(Numeric(precision=20, scale=10), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(), nullable=True, default=datetime.now)
