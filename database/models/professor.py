from peewee import Model, CharField, ForeignKeyField
from database.database import db
from database.models.disciplina import Disciplina

class Professor(Model):
    nome_professor = CharField()
    disciplina = ForeignKeyField(Disciplina, backref='professor', on_delete='RESTRICT', null=True)
    email = CharField()

    class Meta:
        database = db