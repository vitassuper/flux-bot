import traceback
from typing import Union

import ccxt

from src.app import schemas
from src.bot.exceptions.connector_exception import ConnectorException
from src.bot.exchange.bot import Bot
from src.bot.exchange.notifiers.telegram_notifier import TelegramNotifier


class SignalDispatcher:
    def __init__(self):
        self.notifier = TelegramNotifier()
        self.strategy = None

    async def dispatch(self, signal: Union[schemas.AddSignal, schemas.OpenSignal, schemas.CloseSignal]):
        try:
            self.notifier.add_message_to_stack(
                f'Received <b>{signal.type_of_signal}</b> signal: pair: {signal.pair}' + (
                    f' amount: {signal.amount}' if hasattr(signal, 'amount') else ''))

            bot = Bot(bot_id=signal.bot_id, pair=signal.pair, type_of_signal=signal.type_of_signal)

            self.strategy = await bot.process()

            self.notifier.set_exchange_name(bot.get_bot_name())

            match signal.type_of_signal:
                case 'open':
                    await self.handle_open_signal(amount=signal.amount)

                case 'add':
                    await self.handle_average_signal(amount=signal.amount)

                case 'close':
                    await self.handle_close_signal(amount=signal.amount)
                case _:
                    raise ConnectorException('unknown type of signal')

        except ConnectorException as e:
            self.notifier.add_message_to_stack(
                f'🚨Cant {signal.type_of_signal}: {str(e)}')
            traceback.print_tb(e.__traceback__)

        except ccxt.BaseError as ccxt_error:
            self.notifier.add_message_to_stack(f'🚨{str(ccxt_error)}')
            traceback.print_tb(ccxt_error.__traceback__)
        finally:
            await self.notifier.send_message()

    async def handle_open_signal(self, amount: float):
        opened_position_message = await self.strategy.open_deal(amount=amount)

        self.notifier.add_message_to_stack(str(opened_position_message))

    async def handle_average_signal(self, amount: float):
        averaged_position_message = await self.strategy.average_deal(amount=amount)

        self.notifier.add_message_to_stack(str(averaged_position_message))

    async def handle_close_signal(self, amount: float):
        closed_position_message = await self.strategy.close_deal(amount=amount)

        self.notifier.add_message_to_stack(str(closed_position_message))
