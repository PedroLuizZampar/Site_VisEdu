from peewee import Model, CharField
from database.database import db

class Sala(Model): # O Peewee já cria um ID automático, por isso não criamos um
    nome_sala = CharField()

    class Meta:
        database = db