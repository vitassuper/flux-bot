from typing import Union
import ccxt

from src.app import schemas

from src.bot.exception import ConnectorException
from src.bot.exchange.bot import Bot
from src.bot.notifier import Notifier


async def run(signal: Union[schemas.AddSignal, schemas.OpenSignal, schemas.CloseSignal]):
    connector = Connector(bot_id=signal.bot_id)
   
    await connector.dispatch(signal=signal)


class Connector:
    def __init__(self, bot_id: int) -> None:
        self.bot = Bot(bot_id)
        self.strategy = self.bot.get_strategy()

        self.notifier = Notifier(
            exchange_name=f'Bot id: {bot_id} ({self.bot.exchange.get_exchange_name()})')

    async def dispatch(self, signal: Union[schemas.AddSignal, schemas.OpenSignal, schemas.CloseSignal]) -> None:
        try:
            await self.notifier.send_notification(f'Received <b>{signal.type_of_signal}</b> signal: pair: {signal.pair}' + (
                f' amount: {signal.amount}' if hasattr(signal, 'amount') else ''))

            # TODO: temp to check tv ticker
            pair = self.bot.guess_symbol_from_tv(signal.pair)

            match signal.type_of_signal:
                case 'open':
                    await self.dispatch_open_short_position(
                        pair=pair, amount=signal.amount)

                case 'add':
                    await self.dispatch_add_to_short_position(
                        pair=pair, amount=signal.amount)

                case 'close':
                    await self.dispatch_close_short_position(pair=pair)
                case _:
                    raise ConnectorException('unknown type of signal')

        except ConnectorException as e:
            await self.notifier.send_warning_notification(
                f'Cant {signal.type_of_signal}: {str(e)}')

        except ccxt.BaseError as ccxt_error:
            await self.notifier.send_warning_notification(str(ccxt_error))

    async def dispatch_open_short_position(self, pair: str, amount: float):
        opened_position = self.strategy.open_deal(pair=pair, amount=amount)

        await self.notifier.send_notification(
            f'Opened position: {opened_position.pair}, size: {opened_position.quote_amount}$')

    async def dispatch_add_to_short_position(self, pair: str, amount: float):
        averaged_position = self.strategy.average_deal(
            pair=pair, amount=amount)

        await self.notifier.send_notification(
            f'Averaged position, pair: {averaged_position.pair}, size: {averaged_position.quote_amount}$ safety orders: {averaged_position.safety_orders_count}')

    async def dispatch_close_short_position(self, pair: str):
        closed_position = self.strategy.close_deal(pair=pair)

        await self.notifier.send_notification((
            f'{pair}\n'
            f'Profit:{closed_position.profit}💰💰💰 ({closed_position.profit_percentage}%)\n'
            f'Size: {closed_position.quote_amount}$\n'
            f'Duration: {closed_position.duration}\n'
            f'Safety orders: {closed_position.safety_orders_count}'
        ))
