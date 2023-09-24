from src.bot.exceptions.connector_exception import ConnectorException
from src.bot.exchange.side.base_side import BaseSide
from src.bot.types.margin_type import MarginType
from src.bot.types.side_type import SideType


class ShortSide(BaseSide):
    def ensure_deal_not_opened(self, pair: str) -> None:
        open_position = self.exchange.get_opened_short_position(pair)

        if open_position:
            raise ConnectorException(f'the specified position already exists on the exchange: {pair}')

    def ensure_deal_opened(self, pair: str) -> None:
        open_position = self.exchange.get_opened_short_position(pair=pair)

        if not open_position:
            raise ConnectorException(f'the specified position does not exist on the exchange: {pair}')

    def set_leverage(self, pair: str, leverage: int):
        self.exchange.set_leverage_for_short_position(
            pair=pair, leverage=leverage, margin_type=self.margin_type)

    def open_market_order(self, pair: str, amount: float):
        order = self.exchange.sell_short_position(
            pair=pair, amount=amount, margin_type=self.margin_type)

        return self.exchange.get_order_status(order=order, pair=pair)

    def close_market_order(self, pair: str, amount: int):
        order = self.exchange.buy_short_position(
            pair=pair, amount=amount, margin_type=self.margin_type)

        return self.exchange.get_order_status(order=order, pair=pair)

    def add_margin(self, pair: str, quote_amount: float):
        if self.margin_type == MarginType.cross:
            raise ConnectorException(
                'Cant add margin to cross-margined position')

        self.exchange.add_margin_to_short_position(
            pair=pair, amount=quote_amount)

    def get_opened_position(self, pair: str):
        open_position = self.exchange.get_opened_short_position(pair=pair)

        if not open_position:
            raise ConnectorException(f'the specified position does not exist on the exchange: {pair}')

        return open_position

    def get_side_type(self):
        return SideType.short
