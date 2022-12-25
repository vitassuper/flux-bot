from peewee import SqliteDatabase, Model, CharField, DateField

db = SqliteDatabase('connector.db')

class Deal(Model):
    name = CharField()
    birthday = DateField()

    class Meta:
        database = db
