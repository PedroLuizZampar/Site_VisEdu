from peewee import Model, CharField
from database.database import db

class Turma(Model): # O Peewee já cria um ID automático, por isso não criamos um
    nome_turma = CharField()

    class Meta:
        database = db