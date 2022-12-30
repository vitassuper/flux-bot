from sqlalchemy import Column, Integer, String, SmallInteger, Numeric

from src.app.models.base import Base


class Deal(Base):
    id = Column(Integer, primary_key=True, index=True)
    pair = Column(String(255))
    exchangeId = Column(String(255))
    safety_order_count = Column(SmallInteger(), default=0)
    date_open = Column(Integer())
    date_close = Column(Integer(), nullable=True, default=None)
    pnl = Column(Numeric(precision=8), nullable=True)
