from routes.home import home_route
from routes.cadastro import cadastro_route
from routes.upload import upload_route
from routes.sala import sala_route
from routes.turma import turma_route
from routes.disciplina import disciplina_route
from database.database import db
from database.models.upload import Upload
from database.models.sala import Sala
from database.models.analise import Analise
from database.models.horario import Horario
from database.models.turma import Turma
from database.models.periodo import Periodo
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

def configure_db():
    db.connect()
    db.create_tables([Periodo])
    db.create_tables([Sala])
    db.create_tables([Horario])
    db.create_tables([Turma])
    db.create_tables([Disciplina])
    db.create_tables([Upload])
    db.create_tables([Analise])

def create_periodos():
    # Verifica se já existe os períodos definidos, senão os cria
    periodos = ["Matutino", "Vespertino", "Noturno"]
    
    for nome_periodo in periodos:
        if not Periodo.select().where(Periodo.nome_periodo == nome_periodo).exists():
            Periodo.create(nome_periodo=nome_periodo)