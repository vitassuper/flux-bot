from typing import Literal, Union
from src.bot.exception import ConnectorException
from src.bot.exchange.base import BaseExchange
from src.bot.exchange.base_strategy import BaseStrategy


class ShortStrategy(BaseStrategy):
    def __init__(self, bot_id: int, exchange: BaseExchange, margin_type: Union[Literal['cross'], Literal['isolated']] = 'isolated') -> None:
        self.margin_type = margin_type
        super().__init__(bot_id=bot_id, exchange=exchange)

    def ensure_deal_not_opened(self, pair: str) -> None:
        self.exchange.ensure_short_position_not_opened(pair)

    def set_leverage(self, pair: str, leverage: int):
        self.exchange.set_leverage_for_short_position(
            pair=pair, leverage=leverage)

    def ensure_deal_opened(self, pair: str) -> None:
        self.exchange.ensure_short_position_opened(pair=pair)

    def open_market_order(self, pair: str, amount: float):
        order = self.exchange.sell_short_position(
            pair=pair, amount=amount, margin_type=self.margin_type)

        return self.exchange.get_order_status(order=order, pair=pair)

    def close_market_order(self, pair: str, amount: float):
        order = self.exchange.buy_short_position(
            pair=pair, amount=amount, margin_type=self.margin_type)

        return self.exchange.get_order_status(order=order, pair=pair)

    def add_margin(self, pair: str, quote_amount: float):
        if self.margin_type == 'cross':
            raise ConnectorException(
                'Cant add margin to cross-margined position')

        self.exchange.add_margin_to_short_position(
            pair=pair, amount=quote_amount)

    def get_opened_position(self, pair: str):
        return self.exchange.get_opened_short_position(pair=pair)
