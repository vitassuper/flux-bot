import ccxt.async_support as ccxt
from src.bot.exchange.async_base import BaseExchange
from src.core.config import settings


class Binance(BaseExchange):
    def __init__(self, bot_id: int) -> None:
        exchange = ccxt.binance({
            'apiKey': settings.API_KEY_BINANCE,
            'secret': settings.API_SECRET_BINANCE,
            'options': {
                'defaultType': 'future',
            },
            'enableRateLimit': True
        })

        super().__init__(bot_id=bot_id, exchange=exchange)

    def get_exchange_name(self):
        return 'Binance'

    async def fetch_opened_positions(self):
        async with self as exchange:
            exchange_positions = await exchange.fetch_positions_risk()
            exchange_positions = [
                position for position in exchange_positions if position['contracts']]
            exchange_positions.sort(key=lambda item: item["info"]["symbol"])

            return exchange_positions
