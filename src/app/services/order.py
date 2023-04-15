import decimal
from typing import List

from src.app.models.order import Order
from src.app.repositories import order as repository


async def create_order(deal_id: int, side: str, price: decimal, volume: decimal) -> Order:
    return await repository.create_order(deal_id=deal_id, side=side, price=price, volume=volume)


async def get_orders(deal_id: int) -> List[Order]:
    return await repository.get_deal_orders(deal_id=deal_id)


async def get_orders_volume(deal_id: int) -> float:
    return await repository.sum_order_volume(deal_id=deal_id)
