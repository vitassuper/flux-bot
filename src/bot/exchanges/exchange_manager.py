from src.bot.exceptions import ConnectorException
from src.bot.exchanges import Binance, Okex
from src.db.models import Exchange


class ExchangeManager:
    def __init__(self, exchange: Exchange):
        self.exchange = exchange

        self.exchanges = {
            "binance": Binance,
            "okex": Okex,
        }

    def get_exchange(self):
        if self.exchange.type in self.exchanges:
            exchange_class = self.exchanges[self.exchange.type]
            return exchange_class(self.exchange)
        else:
            raise ConnectorException(f"Unsupported exchange type: {self.exchange.type}")
