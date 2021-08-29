from peewee import *


db = PostgresqlDatabase('dict-bot-db', user='postgres', password='123456', host='127.0.0.1', port=5432)


class User(Model):
    external_id = IntegerField()

    class Meta:
        database = db


class Word(Model):
    user = ForeignKeyField(User, backref='words')
    word = CharField()
    translation = CharField()

    class Meta:
        database = db


db.connect()
db.create_tables([User, Word])
