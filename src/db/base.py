# Import all the models, so that Base has them before being
# imported by Alembic
from src.db.base_class import Base
from src.app.models.user import User
