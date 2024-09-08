from peewee import Model, CharField, DateField, TimeField, BooleanField, ForeignKeyField
from database.database import db
from database.models.sala import Sala
from database.models.periodo import Periodo
from database.models.turma import Turma

class Upload(Model):
    nome_arquivo = CharField()
    sala = ForeignKeyField(Sala, backref='uploads', on_delete='RESTRICT')  # Adiciona a chave estrangeira e evita deleção em cascata quando uma sala for deletada
    periodo = ForeignKeyField(Periodo, backref='uploads', on_delete='RESTRICT')
    turma = ForeignKeyField(Turma, backref='uploads', on_delete='RESTRICT', null=True)
    data_registro = DateField()
    hora_registro = TimeField()
    caminho_arquivo = CharField()
    is_analisado = BooleanField(default=False)

    class Meta:
        database = db
