from peewee import Model, CharField, DateField, TimeField, BooleanField
from database.database import db

class Upload(Model): # O Peewee já cria um ID automático, por isso não criamos um
    nome_arquivo = CharField()
    turma = CharField()
    data_registro = DateField()
    hora_registro = TimeField()
    caminho_arquivo = CharField()
    is_analisado = BooleanField(default=False)

    class Meta:
        database = db