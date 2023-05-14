import asyncio
from threading import Thread

from src.bot.signal_dispatcher_factory import SignalDispatcherFactory


def spawn_and_dispatch(signal):
    factory = SignalDispatcherFactory()
    dispatcher = factory.create(signal)

    spawn(dispatcher)


def spawn(dispatcher):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    Thread(target=loop.run_until_complete, args=[dispatcher.dispatch()]).start()
