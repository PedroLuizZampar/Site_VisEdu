from routes.home import home_route
from routes.upload import upload_route
from routes.sala import sala_route
from database.database import db
from database.models.upload import Upload
from database.models.sala import Sala
from database.models.analise import Analise

def configure_all(app):
    configure_routes(app)
    configure_db()

def configure_routes(app):
    app.register_blueprint(home_route) # Prefix = "/"
    app.register_blueprint(upload_route, url_prefix = "/uploads")
    app.register_blueprint(sala_route, url_prefix = "/sala")

def configure_db():
    db.connect()
    db.create_tables([Sala])
    db.create_tables([Upload])
    db.create_tables([Analise])