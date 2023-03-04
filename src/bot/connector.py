from typing import Union
import ccxt

from src.app import schemas

from src.bot.exchange.binance import Binance
from src.bot.exception import ConnectorException
from src.bot.exchange.okx import Okex
from src.bot.notifier import Notifier


class Connector:
    def __init__(self):
        self.notifier = Notifier()

        pass

    def dispatch(self, signal: Union[schemas.AddSignal, schemas.OpenSignal, schemas.CloseSignal]) -> None:
        try:
            exchange = self.get_exchange(signal.bot_id)
            pair = exchange.guess_symbol_from_tv(signal.pair)

            match signal.type_of_signal:
                case 'open':
                    exchange.dispatch_open_short_position(
                        pair, signal.amount)
                case 'close':
                    exchange.dispatch_close_short_position(pair)
                case 'add':
                    exchange.dispatch_add_to_short_position(
                        pair, signal.amount)
                case _:
                    raise ConnectorException('unknown type of signal')

        except ConnectorException as e:
            self.notifier.send_warning_notification(
                f"Cant {signal.type_of_signal}: {str(e)}")
            pass

        except ccxt.BaseError as ccxt_error:
            self.notifier.send_warning_notification(str(ccxt_error))
            pass

    def get_exchange(self, bot_id):
        if bot_id == 1:
            return Okex(bot_id)
        if bot_id == 2:
            return Binance(bot_id)

        raise ConnectorException('Unknown bot id')


connector = Connector()
