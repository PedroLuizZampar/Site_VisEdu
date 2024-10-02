from flask import Blueprint, render_template, session
from funcoes_extras import alterando_sessions_para_false

home_route = Blueprint("home", __name__)

@home_route.route('/')
def home():
    visualizando_index = session.pop('visualizando_index', None)

    alterando_sessions_para_false()
    session['visualizando_index'] = True

    return render_template('index.html', visualizando_index=visualizando_index)