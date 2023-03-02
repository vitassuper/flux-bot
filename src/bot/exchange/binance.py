import ccxt
import rsa
from src.bot.exception import ConnectorException
from src.bot.exchange.base import BaseExchange
from src.core.config import settings


class Binance(BaseExchange):

    def get_exchange_name(self):
        return 'Binance'

    def __init__(self) -> None:
        super().__init__()

        self.exchange = ccxt.binance({
            'apiKey': settings.API_KEY_BINANCE,
            'secret': settings.API_SECRET_BINANCE,
            'options': {
                'defaultType': 'future',
            },
        })

        self.exchange.load_markets()

    def ensure_deal_not_opened(self, pair: str):
        positions = self.exchange.fetch_positions_risk([pair])

        open_position = next(
            (p for p in positions if p['contracts']), None)

        if open_position:
            raise ConnectorException(f"position already exists: {pair}")

    def get_position(self, pair: str):
        positions = self.exchange.fetch_positions_risk([pair])

        open_position = next(
            (p for p in positions if p['contracts']), None)

        if not open_position:
            raise ConnectorException('position not exists')

        return open_position

    def dispatch_open_short_position(self, pair: str, amount: float):
        self.notifier.send_notification(
            f"Received open signal: pair: {pair}, amount: {amount}")

        base_amount = self.get_base_amount(quote_amount=amount, pair=pair)

        self.set_leverage_for_short_position(pair, 7)

        self.sell_short_position(pair, base_amount)

        self.notifier.send_notification(
            f"Opened position: {pair}, amount: {amount}")

    def dispatch_add_to_short_position(self, pair: str, amount: float):
        self.notifier.send_notification(
            f"Received signal type: add, pair: {pair}, amount: {amount}")

        open_position = self.get_position(pair)

        base_amount = self.get_base_amount(quote_amount=amount, pair=pair)

        self.sell_short_position(pair, base_amount)

        self.notifier.send_notification(
            f"Averaged position, pair: {pair}, amount: {amount} safety orders: ")

    def dispatch_close_short_position(self, pair: str):
        self.notifier.send_notification(
            f"Received signal type: close, pair: {pair}")

        open_position = self.get_position(pair)

        order = self.buy_short_position(pair, open_position["contracts"])

        result = self.exchange.fetch_my_trades(
            symbol=pair, params={'limit': 1})[0]

        self.notifier.send_notification((
            f"{pair}\n"
            f"Profit:{result['info']['realizedPnl']}$\n"
            f"Size: {result['info']['qty']}\n"
        ))

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

    # TODO: Implement for okex
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
