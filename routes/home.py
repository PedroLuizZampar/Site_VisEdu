from flask import Blueprint, render_template, session

home_route = Blueprint("home", __name__)

@home_route.route('/')
def home():
    # Busca as sessões e atribui um valor padrão de None caso ainda não estejam ativas
    visualizando_salas = session.pop('visualizando_salas', None)
    visualizando_uploads_nao_analisados = session.pop('visualizando_uploads_nao_analisados', None)
    visualizando_uploads_analisados = session.pop('visualizando_uploads_analisados', None)
    visualizando_turmas = session.pop('visualizando_turmas', None)

    # Validando qual session está ativa no momento
    if visualizando_salas:
        return render_template('index.html', visualizando_salas=visualizando_salas)

    elif visualizando_uploads_nao_analisados:
        return render_template('index.html', visualizando_uploads_nao_analisados=visualizando_uploads_nao_analisados)

    elif visualizando_uploads_analisados:
        return render_template('index.html', visualizando_uploads_analisados=visualizando_uploads_analisados)
    
    elif visualizando_turmas:
        return render_template('index.html', visualizando_turmas=visualizando_turmas)
    
    return render_template('index.html') # Se não ouver um session ativa, retorna a página sem parâmetros