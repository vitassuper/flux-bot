import decimal
from datetime import datetime
from typing import Optional, Union

from sqlalchemy import select, and_, func

from src.app.models.deal import Deal
from src.db.session import get_async_session


async def create_deal(bot_id: int, pair: str, date_open: datetime, position: Union[int, None] = None):
    async with get_async_session() as session:
        deal = Deal(
            bot_id=bot_id,
            pair=pair,
            date_open=date_open,
            position=position
        )
        session.add(deal)
        await session.commit()
        await session.refresh(deal)
        return deal


async def update_deal(deal_id: int, **update_values) -> Deal:
    async with get_async_session() as session:
        deal = await session.get(Deal, deal_id)

        for key, value in update_values.items():
            setattr(deal, key, value)

        await session.commit()
        await session.refresh(deal)

        return deal


async def get_bot_last_deal(bot_id: int, pair: str, position: Union[int, None] = None) -> Deal:
    async with get_async_session() as session:
        query = select(Deal).where(and_(Deal.bot_id == bot_id, Deal.pair == pair, Deal.date_close.is_(None))).order_by(
            Deal.id.desc())

        if position is not None:
            query = query.where(Deal.position == position)

        result = await session.execute(query)

        return result.scalar()


async def get_deal_by_id(deal_id: int) -> Deal:
    async with get_async_session() as session:
        query = select(Deal).where(and_(Deal.id == deal_id, Deal.date_close.is_(None)))
        deals = await session.execute(query)

        return deals.scalar()


async def get_open_deals():
    async with get_async_session() as session:
        query = select(Deal).where(Deal.date_close.is_(None)).order_by(Deal.id.desc())
        deals = await session.execute(query)
        return deals.scalars().all()


async def increment_safety_orders_count(deal_id):
    async with get_async_session() as session:
        deal = await session.get(Deal, deal_id)

        deal.safety_order_count = deal.safety_order_count + 1

        await session.commit()
        await session.refresh(deal)

        return deal.safety_order_count


async def get_pnl_sum(start_date: datetime = None):
    async with get_async_session() as session:
        query = select(func.sum(Deal.pnl)).where(Deal.date_close >= start_date) if start_date else select(
            func.sum(Deal.pnl))

        result = await session.execute(query)

        return result.scalar() or 0
