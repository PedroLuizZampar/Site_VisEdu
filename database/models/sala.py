from peewee import Model, CharField, BooleanField
from database.database import db

class Sala(Model): # O Peewee já cria um ID automático, por isso não criamos um
    nome_sala = CharField()
    is_ativa = BooleanField(default=True)

    class Meta:
        database = db