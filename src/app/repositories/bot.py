from src.app.models import Bot
from src.db.session import get_async_session


async def get_bot(bot_id: int) -> Bot:
    async with get_async_session() as session:
        return await session.get(Bot, bot_id)


async def create_bot(bot_id: int, api_key: str, api_secret: str) -> Bot:
    async with get_async_session() as session:
        bot = Bot(
            id=bot_id,
            enabled=True,
            api_key=api_key,
            api_secret=api_secret
        )
        session.add(bot)
        await session.commit()
        await session.refresh(bot)

        return bot
