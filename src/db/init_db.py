from sqlalchemy.orm import Session

from src.app import repositories, schemas
from src.core.config import settings


def init_db(db: Session) -> None:
    user = repositories.user.get_by_email(db, email=settings.FIRST_SUPERUSER)
    if not user:
        user_in = schemas.UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD
        )
        user = repositories.user.create(db, obj_in=user_in)
