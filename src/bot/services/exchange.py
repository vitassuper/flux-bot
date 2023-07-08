from src.bot.exceptions import NotFoundException
from src.bot.models import Exchange
from src.bot.repositories import exchange as repository


async def get_exchange(exchange_id: int) -> Exchange:
    exchange = await repository.get_exchange(exchange_id=exchange_id)

    if not exchange:
        raise NotFoundException('The exchange with this id does not exist in the system')

    return exchange
