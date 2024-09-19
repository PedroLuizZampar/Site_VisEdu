from peewee import Model, CharField, IntegerField, TimeField
from database.database import db

class Periodo(Model):
    nome_periodo = CharField()
    hora_inicio = TimeField()
    hora_termino = TimeField()
    qtde_aulas = IntegerField()

    class Meta:
        database = db
