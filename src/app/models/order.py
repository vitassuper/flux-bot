from sqlalchemy import Column, ForeignKey, Integer, String, Numeric

from src.app.models.base import Base
from src.app.models.deal import Deal


class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, index=True)
    deal_id = Column(Integer, ForeignKey(Deal.id), nullable=False)
    side = Column(String(10), nullable=False)
    price = Column(Numeric(precision=20, scale=10), nullable=False)
    volume = Column(Numeric(precision=20, scale=10), nullable=False)
