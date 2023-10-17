import ccxt.async_support as ccxt

from src.bot.exchange import BaseExchange
from src.config import settings


class Binance(BaseExchange):
    def __init__(self) -> None:
        exchange = ccxt.binance(
            {
                "apiKey": settings.API_KEY_BINANCE,
                "secret": settings.API_SECRET_BINANCE,
                "options": {
                    "defaultType": "future",
                },
                "enableRateLimit": True,
            }
        )

        super().__init__(exchange=exchange)

    def get_exchange_name(self):
        return "Binance"

    async def fetch_opened_positions(self):
        async with self as exchange:
            exchange_positions = await exchange.fetch_positions_risk()
            exchange_positions = [
                position for position in exchange_positions if position["contracts"]
            ]
            exchange_positions.sort(key=lambda item: item["info"]["symbol"])

            return exchange_positions
