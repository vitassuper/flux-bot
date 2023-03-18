from src.bot.exchange.base import BaseExchange
from src.bot.exchange.base_strategy import BaseStrategy


class LongStrategy(BaseStrategy):
    def __init__(self, bot_id: int, exchange: BaseExchange) -> None:
        super().__init__(bot_id=bot_id, exchange=exchange)

    def ensure_deal_not_opened(self, pair: str) -> None:
        self.exchange.ensure_long_position_not_opened(pair=pair)

    def set_leverage(self, pair: str, leverage: int):
        self.exchange.set_leverage_for_long_position(
            pair=pair, leverage=leverage)

    def ensure_deal_opened(self, pair: str) -> None:
        self.exchange.ensure_long_position_opened(pair=pair)

    def open_market_order(self, pair: str, amount: float):
        order = self.exchange.buy_long_position(pair=pair, amount=amount)

        return self.exchange.get_order_status(order=order, pair=pair)

    def close_market_order(self, pair: str, amount: float):
        order = self.exchange.sell_long_position(pair=pair, amount=amount)

        return self.exchange.get_order_status(order=order, pair=pair)

    def add_margin(self, pair: str, quote_amount: float):
        self.exchange.add_margin_to_long_position(
            pair=pair, amount=quote_amount)

    def get_opened_position(self, pair: str):
        return self.exchange.get_opened_long_position(pair=pair)
