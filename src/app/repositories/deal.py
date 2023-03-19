import datetime
import decimal
from typing import Optional

from sqlalchemy import update, select, and_, func

from src.app.models.deal import Deal
from src.db.session import async_session


async def create_deal(bot_id: int, pair: str, date_open: datetime.datetime, pnl: Optional[decimal] = None):
    async with async_session() as session:
        deal = Deal(
            bot_id=bot_id,
            pair=pair,
            date_open=date_open,
            pnl=pnl
        )
        session.add(deal)
        await session.commit()
        return deal


async def update_deal(deal_id: int, **update_values):
    async with async_session() as session:
        deal = await session.execute(
            update(Deal).values(**update_values).where(Deal.id == deal_id).returning(Deal.date_close)
        )
        await session.commit()
        return deal


async def get_bot_last_deal(bot_id: int, pair: str):
    async with async_session() as session:
        query = select(Deal).where(and_(Deal.bot_id == bot_id, Deal.pair == pair)).order_by(Deal.id.desc())
        deals = await session.execute(query)
        return deals.scalars().all()


async def get_open_deals():
    async with async_session() as session:
        query = select(Deal).where(Deal.date_close.is_(None)).order_by(Deal.id.desc())
        deals = await session.execute(query)
        return deals.scalars().all()


async def increment_safety_orders_count():
    async with async_session() as session:
        query = update(Deal).values(safety_order_count=Deal.safety_order_count + 1)
        result = await session.execute(query)
        await session.commit()
        return result


async def get_pnl_sum(start_date: datetime.datetime = None):
    async with async_session() as session:
        query = select(func.sum(Deal.pnl))

        if start_date:
            query.where(Deal.date_close >= start_date)

        result = await session.execute(query)

        return result.scalars().one_or_none() or 0
