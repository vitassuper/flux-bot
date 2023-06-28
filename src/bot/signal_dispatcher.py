import traceback
from copy import deepcopy
from typing import Union

import ccxt

from src.app import schemas
from src.bot.exceptions.connector_exception import ConnectorException
from src.bot.exchange.bot import Bot
from src.bot.exchange.notifiers.telegram_notifier import TelegramNotifier
from .exceptions.not_found_exception import NotFoundException
from .singal_dispatcher_spawner import spawn_and_dispatch
from src.app.services.deal import get_deal_by_id, get_deal


class SignalDispatcher:
    def __init__(
        self,
        signal: Union[schemas.AddSignal, schemas.OpenSignal, schemas.CloseSignal]
    ):
        self.notifier = TelegramNotifier()
        self.signal = signal
        self.strategy = None

    async def dispatch(self):
        try:
            self.notifier.add_message_to_stack(
                f'Position: {self.signal.position}\n'
                f'Received <b>{self.signal.type_of_signal}</b> signal: pair: {self.signal.pair}' + (
                    f' amount: {self.signal.amount}' if hasattr(self.signal, 'amount') else ''))

            bot = Bot(bot_id=self.signal.bot_id, pair=self.signal.pair, type_of_signal=self.signal.type_of_signal,
                      position=self.signal.position)

            for copy_bot in await bot.get_copy_bots():
                copy_signal = deepcopy(self.signal)
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

        deal = await self.get_deal_from_signal()
        averaged_position_message = await self.strategy.average_deal(amount=self.signal.amount, deal=deal)

        self.notifier.add_message_to_stack(str(averaged_position_message))

    async def handle_close_signal(self):
        deal = await self.get_deal_from_signal()
        closed_position_message = await self.strategy.close_deal(amount=self.signal.amount, deal=deal)

        self.notifier.add_message_to_stack(str(closed_position_message))

    async def get_deal_from_signal(self):
        if self.signal.deal_id:
            return await get_deal_by_id(deal_id=self.signal.deal_id)
        else:
            return await get_deal(bot_id=self.signal.bot_id, pair=self.strategy.pair, position=self.signal.position)
