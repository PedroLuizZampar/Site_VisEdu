from routes.home import home_route
from routes.upload import upload_route
from routes.turma import turma_route
from database.database import db
from database.models.upload import Upload
from database.models.turma import Turma

def configure_all(app):
    configure_routes(app)
    configure_db()

def configure_routes(app):
    app.register_blueprint(home_route) # Prefix = "/"
    app.register_blueprint(upload_route, url_prefix = "/uploads")
    app.register_blueprint(turma_route, url_prefix = "/turma")

def configure_db():
    db.connect()
    db.create_tables([Turma])
    db.create_tables([Upload])