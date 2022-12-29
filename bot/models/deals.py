from peewee import (
    SqliteDatabase,
    Model,
    CharField,
    TimestampField,
    DecimalField,
    SmallIntegerField,
)


db = SqliteDatabase("connector.db")


class Deals(Model):
    pair = CharField(max_length=255)
    exchangeId = CharField(max_length=255)
    safety_order_count = SmallIntegerField(default=0)
    date_open = TimestampField()
    date_close = TimestampField(null=True, default=None)
    pnl = DecimalField(max_digits=12, decimal_places=5, null=True)

    class Meta:
        database = db
