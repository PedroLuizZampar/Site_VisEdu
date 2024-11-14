import os
import tempfile
import cv2
from flask import Blueprint, render_template, redirect, url_for, flash, session, request
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

@config_route.route('/form_verificar_fps')
def form_verificar_fps():
    
    return render_template("/configuracoes/configuracoes_templates/form_verificar_fps.html")

@config_route.route('/verificar_fps', methods=["POST"])
def verificar_fps():
    f = request.files['file']
    
    if f:
        # Cria um arquivo temporário no sistema e salva o vídeo
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
            temp_path = temp_file.name
            f.save(temp_path)
        
        # Carrega o vídeo
        cap = cv2.VideoCapture(temp_path)

        # Verifica se o vídeo foi carregado corretamente
        if not cap.isOpened():
            flash("Erro na leitura do vídeo", "error")
            os.remove(temp_path)  # Remove o arquivo temporário
            return redirect(request.referrer)

        # Obtém o FPS e o número total de frames
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()  # Libera o vídeo
        os.remove(temp_path)  # Remove o arquivo temporário

        flash(f"FPS do vídeo: {fps}\nTotal de frames: {total_frames}", "error")
        return redirect(request.referrer)
    else:
        flash("Nenhum arquivo foi enviado.", "error")
        return redirect(request.referrer)