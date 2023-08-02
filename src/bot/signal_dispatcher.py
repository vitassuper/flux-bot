import traceback
from copy import deepcopy
from typing import Union

import ccxt

from src.app.schemas import AddSignal, OpenSignal, CloseSignal
from src.bot.exceptions import NotFoundException
from src.bot.exceptions.connector_exception import ConnectorException
from src.bot.exchange.bot import Bot
from src.bot.exchange.notifiers.telegram_notifier import TelegramNotifier
from src.bot.services import get_bot, get_copy_bots, get_exchange
from src.bot.singal_dispatcher_spawner import spawn_and_dispatch
from src.bot.types.bot_side_type import BotSideType


class SignalDispatcher:
    def __init__(self, signal: Union[AddSignal, OpenSignal, CloseSignal]):
        self.notifier = TelegramNotifier()
        self.signal = signal
        self.strategy = None

    async def dispatch(self):
        try:
            bot_model = await get_bot(self.signal.bot_id)
            exchange = await get_exchange(bot_model.exchange_id)

            self.notifier.add_message_to_stack(
                f'[<b>{self.signal.type_of_signal.capitalize()}</b>] '
                f'Bot Id: {bot_model.id} ({exchange.type.capitalize()})'
                f"{'🟥' if bot_model.side == BotSideType.short else '🟩'}\n"
                f'Pos: {self.signal.position}\n'
                f'{self.signal.pair}' + (
                    f' amount: {self.signal.amount}' if hasattr(self.signal, 'amount') else ''))

            bot_model = await get_bot(self.signal.bot_id)

            bot = Bot(bot=bot_model, signal=self.signal)

            for copy_bot in await get_copy_bots(bot_model.id):
                copy_signal = deepcopy(self.signal)
                #TODO: fix bug related to copy signal where provided deal_id because 2 different bots cant have the same deal
                copy_signal.bot_id = copy_bot.id

                spawn_and_dispatch(copy_signal)

            self.strategy = await bot.process()

            self.notifier.set_exchange_name(bot.get_bot_name())

            match self.signal.type_of_signal:
                case 'open':
                    await self.handle_open_signal()

                case 'add':
                    await self.handle_average_signal()

                case 'close':
                    await self.handle_close_signal()
                case _:
                    raise ConnectorException('unknown type of signal')

        except (ConnectorException, NotFoundException) as e:
            self.notifier.add_message_to_stack(
                f'Bot id: {self.signal.bot_id}\n'
                f'🚨Cant {self.signal.type_of_signal}: {str(e)}')
            traceback.print_tb(e.__traceback__)

        except ccxt.BaseError as ccxt_error:
            self.notifier.add_message_to_stack(f'🚨{str(ccxt_error)}')
            traceback.print_tb(ccxt_error.__traceback__)
        finally:
            await self.notifier.send_message()

    async def handle_open_signal(self):
        opened_position_message = await self.strategy.open_deal(amount=self.signal.amount)

        self.notifier.add_message_to_stack(str(opened_position_message))

    async def handle_average_signal(self):
        ### get_or_create_deal
        averaged_position_message = await self.strategy.average_deal(amount=self.signal.amount)

        self.notifier.add_message_to_stack(str(averaged_position_message))

    async def handle_close_signal(self):
        closed_position_message = await self.strategy.close_deal(amount=self.signal.amount)

        self.notifier.add_message_to_stack(str(closed_position_message))
