from peewee import Model, CharField, ForeignKeyField, IntegerField
from database.database import db
from database.models.upload import Upload

class Analise(Model):
    nome_analise = CharField()
    upload = ForeignKeyField(Upload, backref='analises', on_delete='CASCADE')  # Adiciona a chave estrangeira
    qtde_objetos = IntegerField()
    qtde_objeto_dormindo = IntegerField()
    qtde_objeto_prestando_atencao = IntegerField()
    qtde_objeto_mexendo_celular = IntegerField()
    qtde_objeto_copiando = IntegerField()
    qtde_objeto_disperso = IntegerField()
    qtde_objeto_trabalho_em_grupo = IntegerField()

    class Meta:
        database = db
