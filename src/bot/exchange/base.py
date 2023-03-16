import abc
from datetime import datetime
import re
from src.app.schemas.deals import DealCreate, DealUpdate
from src.app.services.deal import create_deal, get_deal, increment_safety_orders_count, update_deal
from src.bot.helper import calculate_position_pnl_for_position, get_time_duration_string
from src.bot.notifier import Notifier
from src.bot.objects.averaged_position import AveragedPosition
from src.bot.objects.closed_position import ClosedPosition
from src.bot.objects.opened_position import OpenedPosition
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
        market = self.exchange.market(order['symbol'])

        amount = order['amount'] * market['contractSize']

        entry_value = position['entryPrice'] * amount
        exit_value = order['average'] * amount

        u_pnl = exit_value - entry_value

        open_fee = position['entryPrice'] * amount * market['taker']
        close_fee = order['average'] * amount * market['taker']

        if position['side'] == 'short':
            u_pnl = u_pnl * -1

        return u_pnl - open_fee - close_fee

    def calculate_pnl_percentage(self, position, order):
        return calculate_position_pnl_for_position(
            order['average'], position['entryPrice'], float(
                position['leverage']), position['side']
        )

    def dispatch_open_short_position(self, pair: str, amount: float):
        self.ensure_deal_not_opened(pair)

        self.set_leverage_for_short_position(pair, 20)

        base_amount = self.get_base_amount(symbol=pair, quote_amount=amount)

        order = self.sell_short_position(pair=pair, amount=base_amount)

        # TODO: it necessary for OKEX
        order = self.get_order_status(order, pair)

        market = self.exchange.market(order['symbol'])
        quote_amount = order['amount'] * \
            market['contractSize'] * order['average']

        # TODO: only for okex, should be refactored
        if self.bot_id == 1:
            self.add_margin_to_short_position(pair, quote_amount * 0.06)

        create_deal(DealCreate(bot_id=self.bot_id,
                    pair=order['symbol'], date_open=datetime.now()))

        return OpenedPosition(pair=pair, quote_amount=self.exchange.cost_to_precision(order['symbol'], quote_amount))

    def dispatch_close_short_position(self, pair: str):
        open_position = self.get_opened_position(pair=pair)

        order = self.buy_short_position(pair, open_position["contracts"])

        # TODO: it necessary for OKEX
        order = self.get_order_status(order, pair)

        deal = get_deal(self.bot_id, pair=pair)

        pnl = self.calculate_realized_pnl(open_position, order)
        pnl_percentage = self.calculate_pnl_percentage(open_position, order)

        update_deal(bot_id=self.bot_id, pair=pair, obj_in=DealUpdate(
            pnl=pnl, date_close=datetime.now()))

        duration = get_time_duration_string(
            deal.date_open, datetime.fromtimestamp(datetime.now().timestamp()))

        market = self.exchange.market(order['symbol'])
        quote_amount = order['amount'] * \
            market['contractSize'] * order['average']

        return ClosedPosition(
            pair=pair,
            quote_amount=self.exchange.cost_to_precision(
                order['symbol'], quote_amount),
            safety_orders_count=deal.safety_order_count,
            duration=duration,
            profit=self.exchange.decimal_to_precision(pnl, TRUNCATE, 4),
            profit_percentage=pnl_percentage
        )

    def dispatch_add_to_short_position(self, pair: str, amount: float):
        open_position = self.get_opened_position(pair=pair)

        base_amount = self.get_base_amount(symbol=pair, quote_amount=amount)

        order = self.sell_short_position(pair, base_amount)

        # TODO: it necessary for OKEX
        order = self.get_order_status(order, pair)

        market = self.exchange.market(order['symbol'])
        quote_amount = order['amount'] * \
            market['contractSize'] * order['average']

        # TODO: only for okex, should be refactored
        if self.bot_id == 1:
            self.add_margin_to_short_position(pair, quote_amount * 0.06)

        safety_count = increment_safety_orders_count(
            bot_id=self.bot_id, pair=pair)

        return AveragedPosition(
            pair=pair,
            quote_amount=self.exchange.cost_to_precision(
                order['symbol'], quote_amount),
            safety_orders_count=safety_count
        )

    # TODO: temp solution
    def guess_symbol_from_tv(self, symbol: str):
        base = symbol.split("USDT")[0]
        base = re.sub(r"[^a-zA-Z\d]+", "", base)

        return self.exchange.market(f'{base}/USDT:USDT')['id']
