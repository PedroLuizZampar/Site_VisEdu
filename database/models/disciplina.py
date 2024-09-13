from peewee import Model, CharField
from database.database import db

class Disciplina(Model): # O Peewee já cria um ID automático, por isso não criamos um
    nome_disciplina = CharField()

    class Meta:
        database = db