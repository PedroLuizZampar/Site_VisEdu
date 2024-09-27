from peewee import Model, ForeignKeyField
from database.database import db
from database.models.turma import Turma
from database.models.professor import Professor
from database.models.aula import Aula

class Aula_Professor(Model):
    turma = ForeignKeyField(Turma, backref='aula_professor', on_delete='RESTRICT', null=True)  # Adiciona a chave estrangeira e evita deleção em cascata quando uma sala for deletada
    professor = ForeignKeyField(Professor, backref='aula_professor', on_delete='RESTRICT', null=True)
    aula = ForeignKeyField(Aula, backref='aula_professor', on_delete='RESTRICT', null=True)

    class Meta:
        database = db
