import os, time
import cv2
from peewee import DoesNotExist, fn
from ultralytics import YOLO
from moviepy.editor import VideoFileClip
from datetime import datetime, timedelta
from flask import Blueprint, url_for, render_template, redirect, send_from_directory, flash, jsonify, session, request
from werkzeug.utils import secure_filename
from database.models.upload import Upload
from database.models.sala import Sala
from database.models.analise import Analise
from database.models.periodo import Periodo
from database.models.turma import Turma
from database.models.aula import Aula
from funcoes_extras import alterando_sessions_para_false

upload_route = Blueprint("upload", __name__)

cancelado = False

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
AI_FOLDER = os.path.join(os.getcwd(), 'static', 'ai_models')

ALLOWED_EXTENSIONS = {'asf', 'avi', 'm4v', 'mkv', 'mov', 'mp4', 'mpeg', 'mpg', 'ts', 'wmv', 'webm'}

progress_dict = {}  # Dicionário para armazenar o progresso de cada upload

# Verifica se a pasta de uploads existe, se não, cria a pasta
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Verifica se a pasta de modelos de IA existe, se não, cria a pasta
if not os.path.exists(AI_FOLDER):
    os.makedirs(AI_FOLDER)

def allowed_file(filename):
    return '.' in filename and \
    filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def gerar_nome_unico(directory, filename):
    base, extension = os.path.splitext(filename)
    counter = 1
    new_filename = filename

    while os.path.exists(os.path.join(directory, new_filename)):
        new_filename = f"{base}[{counter}]{extension}" # define um novo nome para o arquivo (EX: já tinha 'teste'. Novo arquivo: 'teste[1]')
        counter += 1

    return new_filename

@upload_route.route('/')
def tela_uploads():
    visualizando_uploads = session.pop('visualizando_uploads', None)
    visualizando_uploads_analisados = session.pop('visualizando_uploads_analisados', None)
    visualizando_uploads_nao_analisados = session.pop('visualizando_uploads_nao_analisados', None)

    session['visualizando_uploads'] = True

    return render_template('/upload/index.html', visualizando_uploads=visualizando_uploads, visualizando_uploads_analisados=visualizando_uploads_analisados, visualizando_uploads_nao_analisados=visualizando_uploads_nao_analisados)

@upload_route.route('/nao_analisados')
def lista_uploads_nao_analisados():

    """ Renderiza a lista de uploads NÃO ANALISADOS """

    uploads = Upload.select()

    alterando_sessions_para_false()
    session['visualizando_uploads_nao_analisados'] = True

    uploads_nao_analisados = []

    for upload in uploads:
        if upload.is_analisado == 0:
            uploads_nao_analisados.append(upload)

    return render_template("upload/upload_templates/lista_uploads_nao_analisados.html", uploads=uploads_nao_analisados)

@upload_route.route('/analisados')
def lista_uploads_analisados():

    """ Renderiza a lista de uploads ANALISADOS """

    uploads = Upload.select()

    alterando_sessions_para_false()
    session['visualizando_uploads_analisados'] = True

    uploads_analisados = []

    for upload in uploads:
        if upload.is_analisado == 1:
            uploads_analisados.append(upload)

    return render_template("upload/upload_templates/lista_uploads_analisados.html", uploads=uploads_analisados)

@upload_route.route('/', methods=["POST"])
def inserir_upload():

    """ Adiciona um upload """

    f = request.files['file']

    if f and allowed_file(f.filename):
        basepath = os.path.dirname(__file__)
        data = request.form

        # Recuperar a instância de Sala e do Período com base no nome fornecido no formulário
        sala = Sala.get(Sala.nome_sala == data['sala'])
        periodo = Periodo.get(Periodo.nome_periodo == data['periodo'])

        try:
            turma = Turma.get(Turma.sala == sala, Turma.periodo == periodo)
        except DoesNotExist:
            turma = None

        # Verificação de hora: Certificar que a hora_registro está dentro dos limites do período
        hora_registro = datetime.strptime(data['hora_registro'], "%H:%M").time()

        if not (periodo.hora_inicio <= hora_registro <= periodo.hora_termino):
            flash(f"A hora de registro ({data['hora_registro']}) está fora do período selecionado!", "error")
            return redirect(request.referrer)

        # Substituir espaços por underlines
        nome_arquivo = data['nome_arquivo'].replace(' ', '_')

        # Usa o nome fornecido pelo usuário no formulário
        filename = secure_filename(data['nome_arquivo'])
        old_caminho_arquivo = os.path.abspath(os.path.join(basepath, os.pardir, 'uploads', filename))

        base, extension = os.path.splitext(filename)
        nome_arquivo = f"{base}{extension}"

        nome_arquivo = gerar_nome_unico(os.path.dirname(old_caminho_arquivo), nome_arquivo)

        caminho_arquivo = os.path.abspath(os.path.join(basepath, os.pardir, 'uploads', nome_arquivo))
        
        f.save(caminho_arquivo)  # Salva o arquivo após a verificação

        # Obter a duração do vídeo
        video = VideoFileClip(caminho_arquivo)
        duracao = video.duration  # Duração em segundos
        video.close()  # Fechar o arquivo para liberar recursos

        # Calcular a hora de término com base na duração
        hora_registro_dt = datetime.strptime(data['hora_registro'], "%H:%M")
        duracao_timedelta = timedelta(seconds=duracao)
        hora_termino_dt = hora_registro_dt + duracao_timedelta
        hora_termino = hora_termino_dt.time()

        aulas = Aula.select().where(periodo == periodo)

        aula_upload = None
        for aula in aulas:
            if aula.hora_inicio <= hora_registro <= aula.hora_termino:
                aula_upload = aula
                break

        if hora_termino > aula_upload.hora_termino:
            if os.path.exists(caminho_arquivo):
                os.remove(caminho_arquivo) # Deleta o arquivo salvo na pasta
            else:
                pass
            flash(f"O vídeo não pode ser salvo, pois excede o tempo de uma aula!", "error")
            return redirect(request.referrer)

        # Criar o registro de upload
        Upload.create(
            nome_arquivo=nome_arquivo,
            sala=sala,  # Passar a instância de Sala aqui
            periodo=periodo,
            turma=turma,
            data_registro=data['data_registro'],
            hora_registro=data['hora_registro'],
            caminho_arquivo=caminho_arquivo,
            duracao=duracao,
            hora_termino=hora_termino
        )

        return redirect(url_for('upload.tela_uploads'))
    else:
        flash("Arquivo não permitido!")
        return redirect(request.referrer)

@upload_route.route('/new')
def form_upload():

    """ Renderiza o formulário de uploads """
    
    salas = Sala.select()
    periodos = Periodo.select()

    return render_template("upload/upload_templates/form_upload.html", salas=salas, periodos=periodos)

@upload_route.route('/<int:upload_id>/edit')
def form_edit_upload(upload_id):

    """ Renderiza o formulário de uploads para editar um upload existente """

    upload_selecionado = Upload.get_by_id(upload_id)
    salas = Sala.select()
    periodos = Periodo.select()

    return render_template("upload/upload_templates/form_upload.html", upload=upload_selecionado, salas=salas, periodos=periodos)

@upload_route.route('/<int:upload_id>/update', methods=["POST"])
def atualizar_upload(upload_id):

    """ Atualiza o upload """

    if request.form.get('_method') == 'PUT':
        basepath = os.path.dirname(__file__)
        data = request.form
        f = request.files.get('file')  # Usa .get para evitar KeyError se 'file' não estiver em request.files

        # Obtém o upload a ser atualizado
        upload_editado = Upload.get_by_id(upload_id)
        old_caminho_arquivo = upload_editado.caminho_arquivo
        old_name = upload_editado.nome_arquivo

        # Aplica secure_filename no novo nome do arquivo
        novo_nome_arquivo = secure_filename(data['nome_arquivo'])

        # Recuperar a instância da Sala e do Período com base no nome fornecido no formulário
        sala = Sala.get(Sala.nome_sala == data['sala'])
        periodo = Periodo.get(Periodo.nome_periodo == data['periodo'])

        try:
            turma = Turma.get(Turma.sala == sala, Turma.periodo == periodo)
        except DoesNotExist:
            turma = None

        # Verificação de hora: Certificar que a hora_registro está dentro dos limites do período
        try:
            hora_registro = datetime.strptime(data['hora_registro'], "%H:%M:%S").time()
        except ValueError:
            hora_registro = datetime.strptime(data['hora_registro'], "%H:%M").time()

        if not (periodo.hora_inicio <= hora_registro <= periodo.hora_termino):
            flash(f"A hora de registro ({data['hora_registro']}) está fora do período selecionado!", "error")
            return redirect(request.referrer)

        # Obter a duração do vídeo e o caminho do arquivo
        if f and allowed_file(f.filename):
            # Novo arquivo enviado
            if novo_nome_arquivo == old_name:
                # Substitui o arquivo antigo diretamente
                temp_filename = old_name
                temp_caminho_arquivo = old_caminho_arquivo
            else:
                # Novo arquivo com nome diferente
                temp_filename = novo_nome_arquivo
                temp_caminho_arquivo = os.path.abspath(os.path.join(basepath, os.pardir, 'uploads', temp_filename))
                if os.path.exists(temp_caminho_arquivo) and temp_caminho_arquivo != old_caminho_arquivo:
                    # Se já existe um arquivo com esse nome (e não é o antigo), gera um nome único
                    temp_filename = gerar_nome_unico(os.path.dirname(temp_caminho_arquivo), temp_filename)
                    temp_caminho_arquivo = os.path.abspath(os.path.join(basepath, os.pardir, 'uploads', temp_filename))
            f.save(temp_caminho_arquivo)

            # Obter a duração do novo vídeo
            video = VideoFileClip(temp_caminho_arquivo)
            duracao = video.duration  # Duração em segundos
            video.close()  # Fechar o arquivo para liberar recursos
        else:
            # Nenhum novo arquivo enviado
            if old_name != novo_nome_arquivo:
                # Renomear o arquivo antigo para o novo nome após validação
                temp_filename = novo_nome_arquivo
                temp_caminho_arquivo = os.path.abspath(os.path.join(basepath, os.pardir, 'uploads', temp_filename))
                if os.path.exists(temp_caminho_arquivo) and temp_caminho_arquivo != old_caminho_arquivo:
                    # Se já existe um arquivo com esse nome (e não é o antigo), gera um nome único
                    temp_filename = gerar_nome_unico(os.path.dirname(temp_caminho_arquivo), temp_filename)
                    temp_caminho_arquivo = os.path.abspath(os.path.join(basepath, os.pardir, 'uploads', temp_filename))
            else:
                temp_filename = old_name
                temp_caminho_arquivo = old_caminho_arquivo

            # Obter a duração do vídeo existente
            video = VideoFileClip(old_caminho_arquivo)
            duracao = video.duration  # Duração em segundos
            video.close()  # Fechar o arquivo para liberar recursos

        # Calcular a hora de término com base na duração
        hora_registro_dt = datetime.combine(datetime.today(), hora_registro)
        duracao_timedelta = timedelta(seconds=duracao)
        hora_termino_dt = hora_registro_dt + duracao_timedelta
        hora_termino = hora_termino_dt.time()

        # Verificar se o upload cabe na aula
        aulas = Aula.select().where(Aula.periodo == periodo)
        aula_upload = None
        for aula in aulas:
            if aula.hora_inicio <= hora_registro <= aula.hora_termino:
                aula_upload = aula
                break

        if not aula_upload:
            # Não encontrou uma aula correspondente
            if f and allowed_file(f.filename):
                # Se novo arquivo foi salvo, deletar arquivo temporário
                if os.path.exists(temp_caminho_arquivo) and temp_caminho_arquivo != old_caminho_arquivo:
                    os.remove(temp_caminho_arquivo)
            flash(f"A hora de registro ({data['hora_registro']}) não corresponde a nenhuma aula!", "error")
            return redirect(request.referrer)

        if hora_termino > aula_upload.hora_termino:
            # O vídeo excede o tempo da aula
            if f and allowed_file(f.filename):
                # Deleta o arquivo temporário
                if os.path.exists(temp_caminho_arquivo) and temp_caminho_arquivo != old_caminho_arquivo:
                    os.remove(temp_caminho_arquivo)
            flash(f"O vídeo não pode ser salvo, pois excede o tempo de uma aula!", "error")
            return redirect(request.referrer)

        # Validação passou, agora atualizar o upload
        if f and allowed_file(f.filename):
            # Deleta o arquivo antigo somente agora, se o caminho for diferente
            if os.path.exists(old_caminho_arquivo) and old_caminho_arquivo != temp_caminho_arquivo:
                os.remove(old_caminho_arquivo)
            # Se o arquivo foi salvo em um caminho temporário diferente, já está pronto
            final_caminho_arquivo = temp_caminho_arquivo
            new_filename = temp_filename
        else:
            if old_name != novo_nome_arquivo:
                # Renomeia o arquivo antigo para o novo nome
                if os.path.exists(old_caminho_arquivo):
                    os.rename(old_caminho_arquivo, temp_caminho_arquivo)
                final_caminho_arquivo = temp_caminho_arquivo
                new_filename = temp_filename
            else:
                final_caminho_arquivo = old_caminho_arquivo
                new_filename = old_name

        # Atualiza os campos do upload
        upload_editado.nome_arquivo = new_filename
        upload_editado.caminho_arquivo = final_caminho_arquivo
        upload_editado.duracao = duracao
        upload_editado.hora_termino = hora_termino
        upload_editado.sala = sala
        upload_editado.periodo = periodo
        upload_editado.turma = turma
        upload_editado.data_registro = data['data_registro']
        upload_editado.hora_registro = data['hora_registro']

        upload_editado.save()  # Salva as alterações no banco

        return redirect(url_for('upload.tela_uploads'))

@upload_route.route('/<int:upload_id>/view_on_form')
def reproduzir_video_form(upload_id):

    """ Reproduz o vídeo no formulário """

    upload = Upload.get_by_id(upload_id)
    nome_arquivo = upload.nome_arquivo
    timestamp = int(time.time())  # Adiciona um timestamp como parâmetro de consulta (Isso evita um bug na reprodução do vídeo e não sei o porquê. NÃO REMOVER)

    return render_template('video/video.html', nome_arquivo=nome_arquivo, timestamp=timestamp)

@upload_route.route('/<int:upload_id>/view')
def reproduzir_video_modal(upload_id):

    """ Reproduz o vídeo no modal """

    upload = Upload.get_by_id(upload_id)
    nome_arquivo = upload.nome_arquivo
    timestamp = int(time.time())  # Adiciona um timestamp como parâmetro de consulta (Isso evita um bug na reprodução do vídeo e não sei o porquê. NÃO REMOVER)

    return render_template('video/video.html', nome_arquivo=nome_arquivo, timestamp=timestamp, modal=True)

@upload_route.route('/<filename>')
def uploaded_file(filename):

    """ Busca o arquivo que foi salvo no servidor """

    basepath = os.path.dirname(__file__)
    
    return send_from_directory(os.path.join(basepath, os.pardir, 'uploads'), filename)

@upload_route.route('/<int:upload_id>/delete', methods=["DELETE"])
def deletar_upload(upload_id):

    """ Apaga um upload do sistema """

    upload = Upload.get_by_id(upload_id) # Quando estamos passando o valor de uma classe para uma variável, estamos instanciando ela
    caminho_arquivo = upload.caminho_arquivo

    if os.path.exists(caminho_arquivo):
        os.remove(caminho_arquivo) # Deleta o arquivo salvo na pasta
    else:
        pass

    upload.delete_instance() # Aqui deletamos a instância

    return {"deleted": "ok"}

@upload_route.route('/<int:upload_id>/new_status', methods=["PUT"])
def atualizar_status(upload_id):

    """ Atualiza o status do upload """

    upload = Upload.get_by_id(upload_id)

    upload.is_analisado = 0 if upload.is_analisado == 1 else 1

    upload.save()
    return {"changed": "ok"}

@upload_route.route('/<int:upload_id>/analise', methods=["POST"])
def analisar_upload(upload_id):
    """ Passa o vídeo para a IA fazer a análise """
    global cancelado
    cancelado = False

    deletar_analise(upload_id)  # Apaga as análises anteriores caso tenha

    basepath = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))
    model_path = os.path.abspath(os.path.join(basepath, 'ai_models', 'best.onnx'))
    upload = Upload.get_by_id(upload_id)
    video_path = os.path.expanduser(upload.caminho_arquivo)

    # Carrega o modelo pré-treinado
    model = YOLO(model_path)
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)  # Verifica quantos FPS tem no vídeo

    if not fps or fps == 0:
        flash("Erro ao obter FPS do vídeo!")
        return redirect(request.referrer)

    # Obter o número total de frames do vídeo
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    if not cap.isOpened():
        flash("Erro ao abrir o vídeo!")
        return redirect(request.referrer)

    frame_count = 0
    frame_interval = 1800

    progress_dict['progress'] = 0  # Inicializa o progresso

    while not cancelado and cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        if frame_count % frame_interval == 0:
            identificar(frame, frame_count, fps, upload, model)

        # Calcular a porcentagem de progresso
        progress = (frame_count / total_frames) * 100
        progress_dict['progress'] = progress

    cap.release()
    progress_dict.pop('progress', None)  # Remove o progresso atual

    if not cancelado:
        atualizar_status(upload_id)
        flash("Análise concluída!")
        return jsonify({"upload_id": upload_id})
    else:
        flash("Análise interrompida pelo usuário.")
        return jsonify({"upload_id": upload_id})
    
@upload_route.route('/analise_todos', methods=["POST"])
def analisar_todos():
    """ Passa todos os vídeos para a IA fazer a análise """
    global cancelado
    cancelado = False

    # Obter todos os uploads
    uploads = Upload.select().where(Upload.is_analisado == 0)

    if not uploads:
        return jsonify({"status": "erro", "mensagem": "Nenhum upload encontrado para análise!"}), 400

    basepath = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))
    model_path = os.path.abspath(os.path.join(basepath, 'ai_models', 'best.onnx'))

    # Carrega o modelo pré-treinado uma vez
    model = YOLO(model_path)

    progress_dict['progress'] = 0  # Inicializa o progresso

    # Calcula o total de frames de todos os uploads
    total_frames_all_uploads = 0
    for upload in uploads:
        video_path = os.path.expanduser(upload.caminho_arquivo)
        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        total_frames_all_uploads += total_frames
        cap.release()

    total_frames_processed = 0

    for idx, upload in enumerate(uploads):
        upload_id = upload.id

        deletar_analise(upload_id)  # Apaga as análises anteriores caso tenha
        video_path = os.path.expanduser(upload.caminho_arquivo)

        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)  # Verifica quantos FPS tem no vídeo

        if not fps or fps == 0:
            flash(f"Erro ao obter FPS do vídeo do upload {upload_id}!")
            continue  # Pula para o próximo upload

        # Obter o número total de frames do vídeo
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        if not cap.isOpened():
            flash(f"Erro ao abrir o vídeo do upload {upload_id}!")
            continue  # Pula para o próximo upload

        frame_count = 0
        frame_interval = 1800  # Ajuste conforme necessário

        while not cancelado and cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1
            total_frames_processed += 1

            if frame_count % frame_interval == 0:
                identificar(frame, frame_count, fps, upload, model)

            # Atualiza o progresso total
            progress = (total_frames_processed / total_frames_all_uploads) * 100
            progress_dict['progress'] = progress

        cap.release()

        if not cancelado:
            atualizar_status(upload_id)
            flash(f"Análise do upload {upload_id} concluída!")
        else:
            flash(f"Análise do upload {upload_id} interrompida pelo usuário.")
            break  # Interrompe a análise de todos os uploads

    progress_dict.pop('progress', None)  # Remove o progresso ao finalizar
    flash("Análise de todos os uploads concluída!")
    return jsonify({"status": "concluido", "mensagem": "Análise de todos os uploads concluída!"})

# Função para processar cada frame do vídeo
def identificar(frame, frame_count, fps, upload, model):
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = model.predict(frame_rgb)[0]  # Obtém apenas o primeiro resultado
    high_conf_boxes = []

    # Variáveis para contar as detecções
    qtde_objetos = 0
    qtde_objeto_dormindo = 0
    qtde_objeto_prestando_atencao = 0
    qtde_objeto_mexendo_celular = 0
    qtde_objeto_copiando = 0
    qtde_objeto_disperso = 0
    qtde_objeto_trabalho_em_grupo = 0

    if results.boxes:  # Se há detecções
        for box in results.boxes:
            obj_class = box.cls.item()
            conf = box.conf.item()
            if conf >= 0.2:
                high_conf_boxes.append(box)
                qtde_objetos += 1

                # Incrementa as contagens com base na classe do objeto
                if obj_class == 0:
                    qtde_objeto_dormindo += 1
                elif obj_class == 1:
                    qtde_objeto_prestando_atencao += 1
                elif obj_class == 2:
                    qtde_objeto_mexendo_celular += 1
                elif obj_class == 3:
                    qtde_objeto_copiando += 1
                elif obj_class == 4:
                    qtde_objeto_disperso += 1
                elif obj_class == 5:
                    qtde_objeto_trabalho_em_grupo += 1

        # Calcular o tempo decorrido desde o início do vídeo
        time_offset_seconds = frame_count / fps
        time_offset = timedelta(seconds=time_offset_seconds)

        # Combinar data e hora de registro do upload
        datetime_registro = datetime.combine(upload.data_registro, upload.hora_registro)

        # Calcular a hora da análise a partir do tempo de gravação decorrido
        datetime_analise = datetime_registro + time_offset
        hora_analise = datetime_analise.time()

        Analise.create(
            nome_analise=f"Análise do Frame {frame_count}",
            upload=upload,
            hora_analise=hora_analise,
            qtde_objetos=qtde_objetos,
            qtde_objeto_dormindo=qtde_objeto_dormindo,
            qtde_objeto_prestando_atencao=qtde_objeto_prestando_atencao,
            qtde_objeto_mexendo_celular=qtde_objeto_mexendo_celular,
            qtde_objeto_copiando=qtde_objeto_copiando,
            qtde_objeto_disperso=qtde_objeto_disperso,
            qtde_objeto_trabalho_em_grupo=qtde_objeto_trabalho_em_grupo
        )

@upload_route.route('/progress', methods=['GET'])
def get_progress():
    """ Retorna o progresso da análise em andamento """
    # Não precisamos mais do upload_id
    progress = progress_dict.get('progress', 0)

    # Determina o status com base no progresso
    status = 'em andamento'
    if progress >= 100:
        status = 'concluido'
    elif cancelado:
        status = 'cancelado'

    return jsonify({'progress': progress, 'status': status})

@upload_route.route('/cancelar_analise', methods=["POST"])
def cancelar_analise():
    """ Interrompe a análise em andamento """
    global cancelado
    cancelado = True
    return redirect(url_for('upload.tela_uploads'))

@upload_route.route('<int:upload_id>/deletar_analise', methods=["DELETE"])
def deletar_analise(upload_id):
    analises = Analise.select()
    upload = Upload.get_by_id(upload_id)

    for analise in analises:
        if analise.upload.id == upload_id:
            analise.delete_instance()

    if upload.is_analisado == 1:
        atualizar_status(upload_id)

    return {"analise_deletada": "ok"}

@upload_route.route('/status_analise/<int:upload_id>', methods=["GET"])
def status_analise(upload_id):

    """ Verifica se o upload já foi analisado ou se ainda está no processo de análise """

    upload = Upload.get_by_id(upload_id)
    status = "concluido" if upload.is_analisado else "em_progresso"
    if status:
        return jsonify({'status': status})
    else:
        return jsonify({'error': 'Análise não encontrada'}), 404

@upload_route.route('/<int:upload_id>/opcoes_grafico', methods=["GET"])
def opcoes_grafico(upload_id):

    upload = Upload.get_by_id(upload_id)

    return render_template('/upload/graficos/opcoes_graficos.html', upload=upload)
    
@upload_route.route('/<int:upload_id>/relatorio/media_comportamentos', methods=["GET"])
def media_comportamentos(upload_id):
    query = (Analise
             .select(
                 fn.AVG(Analise.qtde_objeto_dormindo).alias('avg_dormindo'),
                 fn.AVG(Analise.qtde_objeto_prestando_atencao).alias('avg_prestando_atencao'),
                 fn.AVG(Analise.qtde_objeto_mexendo_celular).alias('avg_mexendo_celular'),
                 fn.AVG(Analise.qtde_objeto_copiando).alias('avg_copiando'),
                 fn.AVG(Analise.qtde_objeto_disperso).alias('avg_disperso'),
                 fn.AVG(Analise.qtde_objeto_trabalho_em_grupo).alias('avg_trabalho_em_grupo')
             )
             .where(Analise.upload_id == upload_id)
             .dicts()
             .get())

    labels = [
        "Dormindo", "Prestando Atenção", "Mexendo no Celular",
        "Copiando", "Disperso", "Trabalho em Grupo"
    ]
    data = [
        round(query['avg_dormindo']),
        round(query['avg_prestando_atencao']),
        round(query['avg_mexendo_celular']),
        round(query['avg_copiando']),
        round(query['avg_disperso']),
        round(query['avg_trabalho_em_grupo'])
    ]

    return jsonify({
        'labels': labels,
        'data': data
    })

@upload_route.route('/<int:upload_id>/relatorio/contagem_alunos_comportamentos', methods=["GET"])
def contagem_alunos_comportamentos(upload_id):
    query = (Analise
             .select(
                 fn.SUM(Analise.qtde_objeto_dormindo).alias('total_dormindo'),
                 fn.SUM(Analise.qtde_objeto_prestando_atencao).alias('total_prestando_atencao'),
                 fn.SUM(Analise.qtde_objeto_mexendo_celular).alias('total_mexendo_celular'),
                 fn.SUM(Analise.qtde_objeto_copiando).alias('total_copiando'),
                 fn.SUM(Analise.qtde_objeto_disperso).alias('total_disperso'),
                 fn.SUM(Analise.qtde_objeto_trabalho_em_grupo).alias('total_trabalho_em_grupo')
             )
             .where(Analise.upload_id == upload_id)
             .dicts()
             .get())  # Obtendo a soma total de cada comportamento

    # Listas para armazenar os dados
    labels = [
        "Dormindo", "Prestando Atenção", "Mexendo no Celular",
        "Copiando", "Disperso", "Trabalho em Grupo"
    ]
    data = [
        query['total_dormindo'] or 0,
        query['total_prestando_atencao'] or 0,
        query['total_mexendo_celular'] or 0,
        query['total_copiando'] or 0,
        query['total_disperso'] or 0,
        query['total_trabalho_em_grupo'] or 0
    ]

    # Encontrar a moda
    mode_value = max(data)
    mode_label = labels[data.index(mode_value)]

    return jsonify({
        'labels': labels,
        'data': data,
        'mode_label': mode_label,
        'mode_value': mode_value
    })
