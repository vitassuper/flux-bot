import time

from ccxt import NetworkError

from src.bot.exceptions.connector_exception import ConnectorException


def retry_on_exception(max_retries=3, wait_time=10):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for i in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except NetworkError as e:
                    time.sleep(wait_time)
            raise ConnectorException(f"Max retries ({max_retries}) reached.")

        return wrapper

    return decorator
