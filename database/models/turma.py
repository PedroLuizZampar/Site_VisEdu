from peewee import Model, CharField, DateField, TimeField, ForeignKeyField
from database.database import db
from database.models.sala import Sala

class Turma(Model):
    nome_turma = CharField()
    sala = ForeignKeyField(Sala, backref='turma', on_delete='RESTRICT')  # Adiciona a chave estrangeira e evita deleção em cascata quando uma sala for deletada
    periodo = DateField()
    qtde_alunos = TimeField()

    class Meta:
        database = db
