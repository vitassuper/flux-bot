from src.bot.exceptions.base_exception import BaseConnectorException


class NotFoundException(BaseConnectorException):
    def __init__(self, entity_type: str):
        super().__init__(
            f"{entity_type.capitalize()} with this id does not exist in the system"
        )
