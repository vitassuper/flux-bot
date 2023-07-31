from typing import List

from sqlalchemy import select

from src.bot.models import Bot
from src.db.session import DB


async def get_bot(bot_id: int) -> Bot:
    async with DB().get_session() as session:
        return await session.get(Bot, bot_id)


async def get_copy_bots(bot_id: int) -> List[Bot]:
    async with DB().get_session() as session:
        query = select(Bot).where(Bot.copy_bot_id == bot_id)
        result = await session.execute(query)

        return result.scalars().all()


async def create_bot(bot_id: int, api_key: str, api_secret: str) -> Bot:
    async with DB().get_session() as session:
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
