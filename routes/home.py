from flask import Blueprint, render_template, session

home_route = Blueprint("home", __name__)

@home_route.route('/')
def home():
    # TENTAR IMPLEMENTAR LOOP COM LISTAS PARA VALIDAR SE A SESSION É VERDADEIRA

    visualizando_turmas = session.pop('visualizando_turmas', None)
    visualizando_uploads_nao_analisados = session.pop('visualizando_uploads_nao_analisados', None)
    visualizando_uploads_analisados = session.pop('visualizando_uploads_analisados', None)

    # Validando qual session está ativa no momento
    if visualizando_turmas:
        return render_template('index.html', visualizando_turmas=visualizando_turmas)

    elif visualizando_uploads_nao_analisados:
        return render_template('index.html', visualizando_uploads_nao_analisados=visualizando_uploads_nao_analisados)

    elif visualizando_uploads_analisados:
        return render_template('index.html', visualizando_uploads_analisados=visualizando_uploads_analisados)