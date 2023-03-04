import ccxt
from src.bot.exception import ConnectorException
from src.bot.exchange.base import BaseExchange
from src.core.config import settings


class Binance(BaseExchange):

    def get_exchange_name(self):
        return 'Binance'

    def __init__(self, bot_id: int) -> None:
        exchange = ccxt.binance({
            'apiKey': settings.API_KEY_BINANCE,
            'secret': settings.API_SECRET_BINANCE,
            'options': {
                'defaultType': 'future',
            },
        })

        super().__init__(bot_id=bot_id, exchange=exchange)

    def ensure_deal_not_opened(self, pair: str):
        positions = self.exchange.fetch_positions_risk([pair])

        open_position = next(
            (p for p in positions if p['contracts']), None)

        if open_position:
            raise ConnectorException(f"position already exists: {pair}")

    def get_opened_position(self, pair: str):
        positions = self.exchange.fetch_positions_risk([pair])

        open_position = next(
            (p for p in positions if p['contracts']), None)

        if not open_position:
            raise ConnectorException('position not exists')

        return open_position

    def fetch_opened_positions(self):
        exchange_positions = self.exchange.fetch_positions_risk()
        exchange_positions = [
            position for position in exchange_positions if position['contracts']]
        exchange_positions.sort(key=lambda item: item["info"]["symbol"])

        return exchange_positions

    def get_order_status(self, order, pair):
        return order

    def set_leverage_for_short_position(self, pair: str, leverage: int):
        self.exchange.set_leverage(leverage, pair)

    def buy_short_position(self, pair: str, amount: int):
        return self.exchange.create_order(
            symbol=pair,
            side="buy",
            type="market",
            amount=amount,
        )

    def sell_short_position(self, pair: str, amount: int):
        return self.exchange.create_order(
            symbol=pair,
            side="sell",
            type="market",
            amount=amount,
        )

    def get_base_amount(self, pair: str, quote_amount: float):
        market = self.exchange.market(pair)
        price = self.exchange.fetch_ticker(pair)['last']

        min_notional_filter = next(
            filter(lambda x: x['filterType'] == 'MIN_NOTIONAL', market['info']['filters']))

        min_notional = float(min_notional_filter['notional'])
        minimal_quote_amount = market['limits']['amount']['min'] * price

        minimal_amount = max(minimal_quote_amount, min_notional)

        if (quote_amount < minimal_amount):
            raise ConnectorException(
                f"low amount for pair {pair} - min amount: {minimal_amount}")

        return self.exchange.amount_to_precision(pair, amount=quote_amount / price)
