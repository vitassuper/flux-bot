from src.db.models import Exchange
from src.db.session import DB


async def get_exchange(exchange_id: int) -> Exchange:
    async with DB().get_session() as session:
        return await session.get(Exchange, exchange_id)
