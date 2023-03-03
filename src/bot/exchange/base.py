from src.bot.exception import ConnectorException
from src.bot.notifier import Notifier


class BaseExchange:
    def __init__(self) -> None:
        self.notifier = Notifier(exchange_name=self.get_exchange_name())

    def ensure_deal_not_opened(self, pair: str):
        positions = self.exchange.fetch_positions()

        open_position = next(
            (p for p in positions if p["info"]["instId"] == pair), None)

        if open_position:
            raise ConnectorException(f"position already exists: {pair}")

    def get_open_positions_info():
        pass
