from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.core.config import settings


def get_async_session():
    engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)

    return async_sessionmaker(bind=engine)()
