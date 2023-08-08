from typing import Union

from src.bot.models import Exchange, Bot
from src.bot.types.bot_side_type import BotSideType
from src.schemas import AddSignal, OpenSignal, CloseSignal


class SignalMessage:
    def __init__(
        self,
        signal: Union[AddSignal, OpenSignal, CloseSignal],
        bot: Bot,
        exchange: Exchange,
    ):
        self._signal = signal
        self._bot = bot
        self._exchange = exchange

    def __str__(self) -> str:
        signal_type = self._signal.type_of_signal.capitalize()
        exchange_type = self._exchange.type.capitalize()
        side_icon = '🟥' if self._bot.side == BotSideType.short else '🟩'
        pair_amount = f'{self._signal.pair}' + (
            f' amount: {self._signal.amount}' if hasattr(self._signal, 'amount') else '')

        return (
            f'[<b>{signal_type}</b>] Bot Id: {self._bot.id} ({exchange_type}) {side_icon}\n'
            f'{pair_amount}\n'
            f'Pos: {self._signal.position}'
        )
