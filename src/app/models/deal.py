from sqlalchemy import Column, Integer, String, SmallInteger, Numeric

from src.app.models.base import Base


class Deal(Base):
    __tablename__ = 'deals'

    id = Column(Integer, primary_key=True, index=True)
    pair = Column(String(255))
    exchange_id = Column(String(255))
    safety_order_count = Column(SmallInteger(), default=0)
    date_open = Column(Integer())
    date_close = Column(Integer(), nullable=True, default=None)
    pnl = Column(Numeric(precision=12, scale=5), nullable=True)
