import logging

from src.db.init_db import init_db
from src.db.session import SessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init() -> None:
    logger.info("Creating initial data")
    db = SessionLocal()
    init_db(db)
    logger.info("Initial data created")


def main() -> None:
    init()


if __name__ == "__main__":
    main()
