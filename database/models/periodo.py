from peewee import Model, CharField
from database.database import db

class Periodo(Model):
    nome_periodo = CharField()

    class Meta:
        database = db
