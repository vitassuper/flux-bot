import threading

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.core.config import settings


class DB:
    _instances = threading.local()

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls._instances, 'instance'):
            cls._instances.instance = super().__new__(cls, *args, **kwargs)
            cls._instances.instance.engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)

        return cls._instances.instance

    def get_session(self):
        return async_sessionmaker(bind=self.engine)()

    async def close(self):
        await self.engine.dispose()
