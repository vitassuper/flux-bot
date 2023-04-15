import decimal

from sqlalchemy import select, func

from src.app.models.order import Order
from src.db.session import async_session


async def create_order(deal_id: int, side: str, price: decimal, volume: decimal):
    async with async_session() as session:
        order = Order(
            deal_id=deal_id,
            side=side,
            price=price,
            volume=volume
        )
        session.add(order)
        await session.commit()
        return order


async def get_deal_orders(deal_id: int):
    async with async_session() as session:
        query = select(Order).where(Order.deal_id == deal_id)
        result = await session.execute(query)

        return result.scalars().all()


async def sum_order_volume(deal_id: int):
    async with async_session() as session:
        query = select(func.sum(Order.volume)).where(Order.deal_id == deal_id)
        result = await session.execute(query)
        total_volume = result.scalars().one()

        return total_volume
