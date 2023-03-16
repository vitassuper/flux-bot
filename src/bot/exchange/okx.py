import ccxt
from src.bot.exception import ConnectorException
from src.bot.exchange.base import BaseExchange
from src.core.config import settings


class Okex(BaseExchange):

    def get_exchange_name(self):
        return 'OKEX'

    def __init__(self, bot_id: int) -> None:
        exchange = ccxt.okex({
            "apiKey": settings.API_KEY,
            "secret": settings.API_SECRET,
            "password": settings.API_PASSWORD,
            "options": {
                "defaultType": "swap",
            },
            'enableRateLimit': True
        })

        super().__init__(bot_id=bot_id, exchange=exchange)

    def get_opened_position(self, pair: str):
        positions = self.exchange.fetch_positions()

        open_position = next(
            (p for p in positions if p["symbol"] == pair), None)

        if not open_position:
            raise ConnectorException('position not exists')

        return open_position

    def ensure_deal_not_opened(self, pair: str):
        positions = self.exchange.fetch_positions()

        open_position = next(
            (p for p in positions if p["symbol"] == pair), None)

        if open_position:
            raise ConnectorException(f"position already exists: {pair}")

    def get_base_amount(self, symbol: str, quote_amount: float):
        market = self.exchange.market(symbol)
        price = self.exchange.fetch_ticker(symbol)["last"]

        return int(quote_amount / price / market["contractSize"])

    def fetch_opened_positions(self):
        exchange_positions = self.exchange.fetch_positions()
        exchange_positions.sort(key=lambda item: item["symbol"])

        return exchange_positions

    def get_order_status(self, order, pair):
        return self.exchange.fetch_order(order['id'], pair)

    def add_margin_to_short_position(self, pair: str, amount: float):
        self.exchange.add_margin(symbol=pair, amount=amount,
                                 params={"posSide": "short"})

    def set_leverage_for_short_position(self, pair: str, leverage: int):
        self.exchange.set_leverage(
            leverage=leverage,
            symbol=pair,
            params={"mgnMode": "isolated", "posSide": "short"},
        )

    def sell_short_position(self, pair: str, amount: int):
        return self.exchange.create_market_sell_order(symbol=pair, amount=amount, params={
            "posSide": "short",
            "tdMode": "isolated",
        },)

    def buy_short_position(self, pair: str, amount: int):
        return self.exchange.create_market_buy_order(symbol=pair, amount=amount, params={
            "posSide": "short",
            "tdMode": "isolated",
        })
