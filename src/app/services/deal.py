from datetime import datetime
from typing import List

from src.app.models import Deal
from src.app.repositories import deal as repository
from src.bot.exceptions.not_found_exception import NotFoundException


async def create_deal(bot_id: int, pair: str, date_open: datetime) -> Deal:
    return await repository.create_deal(bot_id=bot_id, pair=pair, date_open=date_open)


async def increment_safety_orders_count(deal_id: int) -> int:
    return await repository.increment_safety_orders_count(deal_id=deal_id)


async def get_deal(bot_id: int, pair: str) -> Deal:
    deal = await repository.get_bot_last_deal(bot_id=bot_id, pair=pair)

    if not deal:
        raise NotFoundException(
            'The deal with this id does not exist in the system')

    return deal


async def get_or_create_deal(bot_id: int, pair: str) -> Deal:
    deal = await repository.get_bot_last_deal(bot_id=bot_id, pair=pair)

    if not deal:
        deal = await repository.create_deal(bot_id=bot_id, pair=pair, date_open=datetime.now())

    return deal


async def get_opened_deals() -> List[Deal]:
    return await repository.get_open_deals()


async def get_total_pnl() -> float:
    return await repository.get_pnl_sum()


async def get_daily_pnl() -> float:
    midnight = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    return await repository.get_pnl_sum(start_date=midnight)


async def update_deal(deal_id: int, date_close: datetime, pnl: float) -> Deal:
    deal = await repository.update_deal(deal_id=deal_id, date_close=date_close, pnl=pnl)

    if not deal:
        raise NotFoundException(
            'The deal with this id does not exist in the system')

    return deal
