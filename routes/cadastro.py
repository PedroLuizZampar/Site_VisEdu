from flask import Blueprint, render_template, session

cadastro_route = Blueprint("cadastro", __name__)

@cadastro_route.route('/')
def tela_cadastro():
    # Busca as sessões e atribui um valor padrão de None caso ainda não estejam ativas
    visualizando_cadastros = session.pop('visualizando_cadastros', None)
    visualizando_salas = session.pop('visualizando_salas', None)
    visualizando_turmas = session.pop('visualizando_turmas', None)
    visualizando_disciplinas = session.pop('visualizando_disciplinas', None)
    visualizando_periodos = session.pop('visualizando_periodos', None)
    visualizando_aulas = session.pop('visualizando_aulas', None)
    visualizando_professores = session.pop('visualizando_professores', None)

    session['visualizando_cadastros'] = True
    
    return render_template('cadastro/index.html', visualizando_cadastros=visualizando_cadastros, visualizando_salas=visualizando_salas, visualizando_turmas=visualizando_turmas, visualizando_disciplinas=visualizando_disciplinas, visualizando_periodos=visualizando_periodos, visualizando_aulas=visualizando_aulas, visualizando_professores=visualizando_professores) # Se não ouver um session ativa, retorna a página sem parâmetros