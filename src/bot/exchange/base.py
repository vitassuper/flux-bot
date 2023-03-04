import abc
from datetime import datetime
import re
from src.app.schemas.deals import DealCreate, DealUpdate
from src.app.services.deal import create_deal, get_deal, get_opened_deals, increment_safety_orders_count, update_deal
from src.bot.helper import calculate_position_pnl_for_position, get_time_duration_string
from src.bot.notifier import Notifier
from src.bot.position import Position
from ccxt.base.decimal_to_precision import TRUNCATE


class BaseExchange(metaclass=abc.ABCMeta):
    def __init__(self, bot_id: int, exchange) -> None:
        self.notifier = Notifier(exchange_name=self.get_exchange_name())
        self.bot_id = bot_id
        self.exchange = exchange

        self.exchange.load_markets()

    # Abstract methods

    @abc.abstractmethod
    def get_exchange_name(self):
        pass

    @abc.abstractmethod
    def ensure_deal_not_opened(self):
        pass

    @abc.abstractmethod
    def get_base_amount(self, symbol: str, quote_amount: float):
        pass

    @abc.abstractmethod
    def fetch_opened_positions(self):
        pass

    @abc.abstractmethod
    def buy_short_position(self, pair: str, amount: int):
        pass

    @abc.abstractmethod
    def sell_short_position(self, pair: str, amount: int):
        pass

    @abc.abstractmethod
    def get_opened_position(self, pair: str):
        pass

    @abc.abstractmethod
    def set_leverage_for_short_position(pair: str, leverage: int):
        pass

    @abc.abstractmethod
    def get_order_status(self, order, pair):
        pass

    # End Abstract methods

    def calculate_realized_pnl(self, position, order):
        amount = order['amount']

        entry_value = position['entryPrice'] * amount
        exit_value = order['average'] * amount

        u_pnl = exit_value - entry_value

        if position['side'] == 'short':
            return u_pnl * -1

        return u_pnl

    def calculate_pnl_percentage(self, position, order):
        return calculate_position_pnl_for_position(
            order['average'], position['entryPrice'], float(
                position['leverage']), position['side']
        )

    def dispatch_open_short_position(self, pair: str, amount: float):
        self.notifier.send_notification(
            f"Received open signal: pair: {pair}, amount: {amount}")

        self.ensure_deal_not_opened(pair)

        self.set_leverage_for_short_position(pair, 20)

        base_amount = self.get_base_amount(symbol=pair, quote_amount=amount)

        self.sell_short_position(pair=pair, amount=base_amount)

        # TODO: only for okex, should be refactored
        if self.bot_id == 1:
            quantity, contracts_cost = self.convert_quote_to_contracts(
                pair, amount)
            self.add_margin_to_short_position(pair, contracts_cost * 0.06)

        create_deal(DealCreate(bot_id=self.bot_id,
                    pair=pair, date_open=datetime.now()))

        self.notifier.send_notification(
            f"Opened position: {pair}, amount: {amount}")

    def dispatch_close_short_position(self, pair: str):
        self.notifier.send_notification(
            f"Received signal type: close, pair: {pair}")

        open_position = self.get_opened_position(pair=pair)

        order = self.buy_short_position(pair, open_position["contracts"])

        # TODO: it necessary for OKEX
        order = self.get_order_status(order, pair)

        deal = get_deal(self.bot_id, pair=pair)

        pnl = self.calculate_realized_pnl(open_position, order)
        pnl_percentage = self.calculate_pnl_percentage(open_position, order)

        update_deal(bot_id=self.bot_id, pair=pair, obj_in=DealUpdate(
            pnl=pnl, date_close=datetime.fromtimestamp(datetime.now().timestamp())))

        duration = get_time_duration_string(
            deal.date_open, datetime.fromtimestamp(datetime.now().timestamp()))

        self.notifier.send_notification((
            f"{pair}\n"
            f"Profit:{self.exchange.decimal_to_precision(pnl, TRUNCATE, 4)}$ ({pnl_percentage}%)\n"
            f"Size: {open_position['contracts']}\n"
            f"Duration: {duration}\n"
            f"Safety orders: {deal.safety_order_count}"
        ))

    def dispatch_add_to_short_position(self, pair: str, amount: float):
        self.notifier.send_notification(
            f"Received signal type: add, pair: {pair}, amount: {amount}")

        open_position = self.get_opened_position(pair=pair)

        base_amount = self.get_base_amount(symbol=pair, quote_amount=amount)

        self.sell_short_position(pair, base_amount)

        # TODO: only for okex, should be refactored
        if self.bot_id == 1:
            quantity, contracts_cost = self.convert_quote_to_contracts(
                pair, amount)
            self.add_margin_to_short_position(pair, contracts_cost * 0.06)

        safety_count = increment_safety_orders_count(
            bot_id=self.bot_id, pair=pair)

        self.notifier.send_notification(
            f"Averaged position, pair: {pair}, amount: {amount} safety orders: {safety_count}")

    def get_open_positions_info(self):
        deals = get_opened_deals()

        exchange_positions = self.fetch_opened_positions()

        tickers = self.exchange.fetch_tickers(
            [item['symbol'] for item in exchange_positions])

        positions = []

        for item in exchange_positions:
            symbol = item['symbol']

            deal = next((x for x in deals if x.pair ==
                        symbol), None)

            positions.append(
                Position(
                    ticker=item['symbol'],
                    margin=self.exchange.decimal_to_precision(
                        item['initialMargin'], TRUNCATE, 4),
                    avg_price=self.exchange.price_to_precision(
                        symbol, item['entryPrice']),
                    current_price=self.exchange.price_to_precision(
                        symbol, tickers[symbol]['last']),
                    liquidation_price=self.exchange.price_to_precision(
                        symbol, item['liquidationPrice']),
                    unrealized_pnl=self.exchange.decimal_to_precision(
                        item['unrealizedPnl'], TRUNCATE, 4) + f" ({round(item['percentage'], 2)}%)",
                    notional_size=self.exchange.decimal_to_precision(
                        item['notional'], TRUNCATE, 3),
                    deal=deal
                ))

        return positions

    # TODO: temp solution
    def guess_symbol_from_tv(self, symbol: str):
        base = symbol.split("USDT")[0]
        base = re.sub(r"[^a-zA-Z\d]+", "", base)

        return self.exchange.market(f'{base}/USDT:USDT')['id']
