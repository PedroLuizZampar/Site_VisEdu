from peewee import Model, IntegerField
from database.database import db

class Configuracoes(Model): # O Peewee já cria um ID automático, por isso não criamos um
    intervalo_analise_em_segundos = IntegerField()

    class Meta:
        database = db