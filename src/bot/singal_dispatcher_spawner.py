import asyncio
import traceback
from threading import Thread
from typing import Union

import ccxt

from src.bot.exceptions import ConnectorException, NotFoundException
from src.bot.exchange.notifiers.telegram_notifier import TelegramNotifier
from src.bot.objects.messages.error_message import ErrorMessage
from src.bot.objects.messages.signal_message import SignalMessage
from src.bot.signal_dispatcher_factory import SignalDispatcherFactory
from src.db.session import DB
from src.schemas import AddSignal, OpenSignal, CloseSignal


async def run(signal: Union[AddSignal, OpenSignal, CloseSignal]):
    # init DB
    db = DB()
    notifier = TelegramNotifier()

    try:
        dispatcher = await SignalDispatcherFactory.create(signal)
        notifier.add_message_to_stack(
            str(SignalMessage(signal=signal, bot=dispatcher.bot, exchange=dispatcher.exchange)))

        notifier.add_message_to_stack(str(await dispatcher.dispatch()))

    except (ConnectorException, NotFoundException, ccxt.BaseError) as e:
        notifier.add_message_to_stack(str(ErrorMessage(signal, e)))

        traceback.print_tb(e.__traceback__)

    finally:
        # close DB connection
        await db.close()

        await notifier.send_message()


async def spawn_and_dispatch(signal: Union[AddSignal, OpenSignal, CloseSignal]):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    Thread(target=loop.run_until_complete, args=[run(signal)]).start()
