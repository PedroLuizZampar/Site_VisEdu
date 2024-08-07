from peewee import Model, CharField, DateField, TimeField
from database.database import db

class Upload(Model): # O Peewee já cria um ID automático, por isso não criamos um
    nome_arquivo = CharField()
    turma = CharField()
    data_registro = DateField()
    hora_registro = TimeField()
    caminho_arquivo = CharField()

    class Meta:
        database = db