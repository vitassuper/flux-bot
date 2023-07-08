from src.bot.models import Exchange
from src.db.session import get_async_session


async def get_exchange(exchange_id: int) -> Exchange:
    async with get_async_session() as session:
        return await session.get(Exchange, exchange_id)
