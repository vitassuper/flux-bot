import asyncio
from threading import Thread

from src.bot.signal_dispatcher_factory import SignalDispatcherFactory
from src.db.session import DB


async def run(dispatcher):
    # init DB
    db = DB()

    try:
        await dispatcher.dispatch()

    finally:
        # close DB connection
        await db.close()
        print('dispose')


def spawn_and_dispatch(signal):
    factory = SignalDispatcherFactory()
    dispatcher = factory.create(signal)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    Thread(target=loop.run_until_complete, args=[run(dispatcher)]).start()
