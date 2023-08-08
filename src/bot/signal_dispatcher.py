from copy import deepcopy
from typing import Union

from src.bot.exceptions.connector_exception import ConnectorException
from src.bot.exchange.bot import Bot
from src.bot.models import Bot as BotModel, Exchange
from src.bot.objects.messages.averaged_deal_message import AveragedDealMessage
from src.bot.objects.messages.closed_deal_message import ClosedDealMessage
from src.bot.objects.messages.opened_deal_message import OpenedDealMessage
from src.bot.services import get_bot, get_copy_bots, get_exchange
from src.bot.singal_dispatcher_spawner import spawn_and_dispatch
from src.schemas import AddSignal, OpenSignal, CloseSignal


class SignalDispatcher:

    def __init__(
        self,
        signal: Union[AddSignal, OpenSignal, CloseSignal],
        bot: BotModel,
        exchange: Exchange
    ):
        self._signal = signal
        self._bot = bot
        self._exchange = exchange

    @property
    def bot(self):
        return self._bot

    @property
    def exchange(self):
        return self._exchange

    @classmethod
    async def create(cls, signal: Union[AddSignal, OpenSignal, CloseSignal]):
        bot = await get_bot(signal.bot_id)
        exchange = await get_exchange(bot.exchange_id)

        return cls(signal=signal, bot=bot, exchange=exchange)

    async def dispatch(self) -> Union[OpenedDealMessage, AveragedDealMessage, ClosedDealMessage]:
        await self.find_and_run_copy_bots()

        bot = Bot(bot=self._bot, signal=self._signal)

        strategy = await bot.process()

        match self._signal.type_of_signal:
            case 'open':
                return await strategy.open_deal(amount=self._signal.amount)

            case 'add':
                return await strategy.average_deal(amount=self._signal.amount)

            case 'close':
                return await strategy.close_deal(amount=self._signal.amount)
            case _:
                raise ConnectorException('unknown type of signal')

    async def find_and_run_copy_bots(self):
        for copy_bot in await get_copy_bots(self._bot.id):
            copy_signal = deepcopy(self._signal)
            # TODO: fix bug related to copy signal where provided deal_id because 2 different bots cant have the same deal
            copy_signal.bot_id = copy_bot.id

            await spawn_and_dispatch(copy_signal)
