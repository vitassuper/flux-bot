import ccxt.async_support as ccxt
from src.bot.exchange.async_base import BaseExchange
from src.core.config import settings


class Okex(BaseExchange):
    def __init__(self, bot_id: int) -> None:
        exchange = ccxt.okex({
            'apiKey': settings.API_KEY,
            'secret': settings.API_SECRET,
            'password': settings.API_PASSWORD,
            'options': {
                'defaultType': 'swap',
            },
            'enableRateLimit': True
        })

        super().__init__(bot_id=bot_id, exchange=exchange)

    def get_exchange_name(self):
        return 'OKEX'

    async def fetch_opened_positions(self):
        async with self as exchange:
            exchange_positions = await exchange.fetch_positions()
            exchange_positions.sort(key=lambda item: item['symbol'])

            return exchange_positions
