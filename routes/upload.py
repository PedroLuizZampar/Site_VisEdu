from flask import Blueprint, render_template, request
from database.upload import UPLOADS

upload_route = Blueprint("upload", __name__)

@upload_route.route('/')
def lista_uploads():
    """" Renderiza a lista de uploads """

    return render_template("lista_uploads.html", uploads=UPLOADS)