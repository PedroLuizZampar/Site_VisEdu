from peewee import Model, CharField, DateField, TimeField, BooleanField, ForeignKeyField
from database.database import db
from database.models.turma import Turma

class Upload(Model):
    nome_arquivo = CharField()
    turma = ForeignKeyField(Turma, backref='uploads', on_delete='CASCADE')  # Adiciona a chave estrangeira
    data_registro = DateField()
    hora_registro = TimeField()
    caminho_arquivo = CharField()
    is_analisado = BooleanField(default=False)

    class Meta:
        database = db
