from decimal import Decimal
from typing import List

from src.app.models.order import Order
from src.app.repositories import order as repository
from src.bot.exceptions.not_found_exception import NotFoundException
from src.bot.objects.deal_stats import DealStats
from src.bot.utils.helper import Helper


async def create_order(deal_id: int, side: str, price: Decimal, volume: Decimal) -> Order:
    return await repository.create_order(deal_id=deal_id, side=side, price=price, volume=volume)


async def get_orders(deal_id: int) -> List[Order]:
    return await repository.get_deal_orders(deal_id=deal_id)


async def get_deal_stats(deal_id: int) -> DealStats:
    orders = await repository.get_deal_orders(deal_id=deal_id)

    if not orders:
        raise NotFoundException('Not found orders')

    return DealStats(average_price=Helper.calculate_average_price(orders=orders),
                     total_volume=Helper.calculate_total_volume(orders=orders))


async def get_orders_volume(deal_id: int) -> float:
    return await repository.sum_order_volume(deal_id=deal_id)
