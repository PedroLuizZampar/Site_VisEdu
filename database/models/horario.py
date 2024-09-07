from peewee import Model, CharField, IntegerField
from database.database import db

class Horario(Model):
    periodo = CharField()
    qtde_aulas = IntegerField()

    class Meta:
        database = db