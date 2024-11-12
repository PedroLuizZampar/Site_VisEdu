from peewee import Model, IntegerField
from database.database import db

class Configuracoes(Model): # O Peewee já cria um ID automático, por isso não criamos um
    qtde_padrao_frames_video = IntegerField()
    intervalo_frames = IntegerField()

    class Meta:
        database = db