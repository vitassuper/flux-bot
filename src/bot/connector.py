from typing import Union
import ccxt

from src.app import schemas

from src.bot.exception import ConnectorException
from src.bot.exchange.bot import Bot
from src.bot.notifier import Notifier


class Connector:
    def dispatch(self, signal: Union[schemas.AddSignal, schemas.OpenSignal, schemas.CloseSignal]) -> None:
        try:
            bot = Bot(signal.bot_id)
            self.strategy = bot.get_strategy()

            self.exchange = self.strategy.exchange

            self.notifier = Notifier(
                exchange_name=f'Bot id: {signal.bot_id} ({self.exchange.get_exchange_name()})')

            # TODO: temp to check tv ticker
            self.notifier.send_notification(f'Received <b>{signal.type_of_signal}</b> signal: pair: {signal.pair}' + (
                f' amount: {signal.amount}' if hasattr(signal, 'amount') else ''))

            pair = bot.guess_symbol_from_tv(signal.pair)

            match signal.type_of_signal:
                case 'open':
                    self.dispatch_open_short_position(
                        pair=pair, amount=signal.amount)

                case 'add':
                    self.dispatch_add_to_short_position(
                        pair=pair, amount=signal.amount)

                case 'close':
                    self.dispatch_close_short_position(pair=pair)
                case _:
                    raise ConnectorException('unknown type of signal')

        except ConnectorException as e:
            self.notifier.send_warning_notification(
                f'Cant {signal.type_of_signal}: {str(e)}')
            pass

        except ccxt.BaseError as ccxt_error:
            self.notifier.send_warning_notification(str(ccxt_error))
            pass

    def dispatch_open_short_position(self, pair: str, amount: float):
        opened_position = self.strategy.open_deal(pair=pair, amount=amount)

        self.notifier.send_notification(
            f'Opened position: {opened_position.pair}, size: {opened_position.quote_amount}$')

    def dispatch_add_to_short_position(self, pair: str, amount: float):
        averaged_position = self.strategy.average_deal(
            pair=pair, amount=amount)

        self.notifier.send_notification(
            f'Averaged position, pair: {averaged_position.pair}, size: {averaged_position.quote_amount}$ safety orders: {averaged_position.safety_orders_count}')

    def dispatch_close_short_position(self, pair: str):
        closed_position = self.strategy.close_deal(pair=pair)

        self.notifier.send_notification((
            f'{pair}\n'
            f'Profit:{closed_position.profit}💰💰💰 ({closed_position.profit_percentage}%)\n'
            f'Size: {closed_position.quote_amount}$\n'
            f'Duration: {closed_position.duration}\n'
            f'Safety orders: {closed_position.safety_orders_count}'
        ))


connector = Connector()
