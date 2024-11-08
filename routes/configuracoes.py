from flask import Blueprint, render_template, session
from funcoes_extras import alterando_sessions_para_false
from database.models.configuracoes import Configuracoes

config_route = Blueprint("configuracoes", __name__)

@config_route.route('/')
def tela_configuracoes():
    visualizando_config = session.pop('visualizando_config', None)

    alterando_sessions_para_false()
    session['visualizando_index'] = True

    return render_template('configuracoes/index.html', visualizando_config=visualizando_config)

@config_route.route('/lista_configuracoes')
def lista_configuracoes():
    configuracao = Configuracoes.get_or_none(Configuracoes.id == 1)
    
    return render_template('configuracoes/configuracoes_templates/lista_configuracoes.html', configuracao=configuracao)