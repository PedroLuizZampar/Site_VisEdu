from datetime import time
from routes.home import home_route
from routes.cadastro import cadastro_route
from routes.upload import upload_route
from routes.sala import sala_route
from routes.turma import turma_route
from routes.disciplina import disciplina_route
from routes.periodo import periodo_route
from routes.aula import aula_route
from routes.professor import professor_route
from routes.relatorio import relatorio_route
from database.database import db
from database.models.upload import Upload
from database.models.sala import Sala
from database.models.analise import Analise
from database.models.turma import Turma
from database.models.periodo import Periodo
from database.models.aula import Aula
from database.models.professor import Professor
from database.models.aula_professor import Aula_Professor
from database.models.disciplina import Disciplina

def configure_all(app):
    configure_routes(app)
    configure_db()
    create_periodos()

def configure_routes(app):
    app.register_blueprint(home_route) # Prefix = "/"
    app.register_blueprint(cadastro_route, url_prefix="/cadastro")
    app.register_blueprint(upload_route, url_prefix = "/upload")
    app.register_blueprint(sala_route, url_prefix = "/cadastro/sala")
    app.register_blueprint(turma_route, url_prefix="/cadastro/turma")
    app.register_blueprint(disciplina_route, url_prefix="/cadastro/disciplina")
    app.register_blueprint(periodo_route, url_prefix="/cadastro/periodo")
    app.register_blueprint(aula_route, url_prefix="/cadastro/aula")
    app.register_blueprint(professor_route, url_prefix = "/cadastro/professor")
    app.register_blueprint(relatorio_route, url_prefix = "/relatorio")

def configure_db():
    db.connect()
    db.create_tables([Periodo])
    db.create_tables([Aula])
    db.create_tables([Sala])
    db.create_tables([Turma])
    db.create_tables([Disciplina])
    db.create_tables([Professor])
    db.create_tables([Aula_Professor])
    db.create_tables([Upload])
    db.create_tables([Analise])

def create_periodos():
    # Verifica se já existe os períodos definidos, senão os cria
    periodos = ["Matutino", "Vespertino", "Noturno"]
    
    cont = 1

    for nome_periodo in periodos:
        if not Periodo.select().where(Periodo.nome_periodo == nome_periodo).exists():
            if cont == 1:
                Periodo.create(nome_periodo=nome_periodo, hora_inicio=time(7, 20, 00), hora_termino=time(12, 35, 00), qtde_aulas=1)
                Aula.create(periodo=Periodo.select().where(Periodo.nome_periodo == nome_periodo), hora_inicio=time(7, 20, 00), hora_termino=time(8, 10, 00))
            elif cont == 2:
                Periodo.create(nome_periodo=nome_periodo, hora_inicio=time(13, 10, 00), hora_termino=time(18, 35, 00), qtde_aulas=1)
                Aula.create(periodo=Periodo.select().where(Periodo.nome_periodo == nome_periodo), hora_inicio=time(13, 10, 00), hora_termino=time(14, 00, 00))
            else:
                Periodo.create(nome_periodo=nome_periodo, hora_inicio=time(19, 30, 00), hora_termino=time(23, 55, 00), qtde_aulas=1)
                Aula.create(periodo=Periodo.select().where(Periodo.nome_periodo == nome_periodo), hora_inicio=time(19, 30, 00), hora_termino=time(20, 20, 00))
            cont += 1