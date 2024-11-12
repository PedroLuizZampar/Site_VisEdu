from flask import Blueprint, render_template, redirect, url_for, session, request
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

@config_route.route('/form_configuracoes')
def form_configuracoes():
    configuracao = Configuracoes.get_or_none(Configuracoes.id == 1)

    return render_template('/configuracoes/configuracoes_templates/form_configuracoes.html', configuracao=configuracao)

@config_route.route('configuracao-<int:configuracao_id>/update', methods=["POST"])
def atualizar_configuracoes(configuracao_id):
    if request.form.get('_method') == "PUT":
        data = request.form

        configuracao = Configuracoes.get_by_id(configuracao_id)

        configuracao_editada = configuracao

        configuracao_editada.qtde_padrao_frames_video = data['qtde_frames']
        configuracao_editada.intervalo_frames = int(data['delay']) * int(data['qtde_frames'])

        configuracao_editada.save()

    return redirect(url_for('configuracoes.tela_configuracoes'))