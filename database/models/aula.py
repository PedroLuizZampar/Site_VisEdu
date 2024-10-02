from peewee import Model, CharField, TimeField, ForeignKeyField
from database.database import db
from database.models.periodo import Periodo

class Aula(Model):
    periodo = ForeignKeyField(Periodo, backref='aula', on_delete='RESTRICT')
    hora_inicio = TimeField()
    hora_termino = TimeField()

    class Meta:
        database = db
