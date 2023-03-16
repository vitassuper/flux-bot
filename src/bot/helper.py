from datetime import datetime
from decimal import Decimal

from src.bot.exception import ConnectorException


def get_time_duration_string(date_open: datetime, date_close: datetime) -> str:
    diff = date_close - date_open
    seconds = int(diff.total_seconds())

    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)

    return f"{int(days)} days, {int(hours)} hours, {int(minutes)} minutes, {int(seconds)} seconds"


def calculate_pnl_percentage(closePrice, avgPrice):
    return Decimal(
        ((closePrice - avgPrice) / avgPrice) * 100
    ).quantize(Decimal("0.01"))


def calculate_position_pnl_percentage(closePrice, avgPrice, leverage):
    return calculate_pnl_percentage(closePrice, avgPrice) * Decimal(leverage)


def calculate_position_pnl_for_position(close_price, avg_price, leverage, pos_side):
    return calculate_position_pnl_percentage(close_price, avg_price, leverage) * get_percentage_sign(pos_side)


def calculate_pnl_for_position(close_price, avg_price, pos_side):
    return calculate_pnl_percentage(close_price, avg_price) * get_percentage_sign(pos_side)


def get_percentage_sign(pos_side):
    if pos_side == "short":
        return -1
    if pos_side == "long":
        return 1

    raise ConnectorException('undefined position direction')
