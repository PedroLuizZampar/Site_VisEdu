from peewee import Model, CharField, IntegerField, ForeignKeyField
from database.database import db
from database.models.sala import Sala
from database.models.periodo import Periodo

class Turma(Model):
    nome_turma = CharField()
    sala = ForeignKeyField(Sala, backref='turma', on_delete='RESTRICT')  # Adiciona a chave estrangeira e evita deleção em cascata quando uma sala for deletada
    periodo = ForeignKeyField(Periodo, backref='turma', on_delete='RESTRICT')  # Adiciona a chave estrangeira e evita deleção em cascata quando uma sala for deletada
    qtde_alunos = IntegerField()

    class Meta:
        database = db
