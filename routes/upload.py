import os, time
import cv2
from ultralytics import YOLO
from flask import Blueprint, url_for, render_template, redirect, send_from_directory, flash, session, request
from werkzeug.utils import secure_filename
from database.models.upload import Upload
from database.models.sala import Sala
from database.models.analise import Analise
from funcoes_extras import alterando_sessions_para_false

upload_route = Blueprint("upload", __name__)

cancelado = False

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
AI_FOLDER = os.path.join(os.getcwd(), 'static', 'ai_models')

ALLOWED_EXTENSIONS = {'asf', 'avi', 'm4v', 'mkv', 'mov', 'mp4', 'mpeg', 'mpg', 'ts', 'wmv', 'webm'}

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

    has_nao_analisado = True # Passa como parâmetro True para renderizar o conteúdo da maneira correta, ou seja, são uploads não analisados
    
    return render_template("lista_uploads.html", uploads=uploads_nao_analisados, has_nao_analisado=has_nao_analisado)

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

    return render_template("lista_uploads.html", uploads=uploads_analisados)

@upload_route.route('/', methods=["POST"])
def inserir_upload():

    """ Adiciona um upload """

    f = request.files['file']

    if f and allowed_file(f.filename):
        basepath = os.path.dirname(__file__)
        data = request.form

        # Substituir espaços por underlines
        nome_arquivo = data['nome_arquivo'].replace(' ', '_')

        # Usa o nome fornecido pelo usuário no formulário
        filename = secure_filename(data['nome_arquivo'])
        old_caminho_arquivo = os.path.abspath(os.path.join(basepath, os.pardir, 'uploads', filename))

        base, extension = os.path.splitext(filename)

        nome_arquivo = f"{base}{extension}"

        nome_arquivo = gerar_nome_unico(os.path.dirname(old_caminho_arquivo), nome_arquivo)

        caminho_arquivo = os.path.abspath(os.path.join(basepath, os.pardir, 'uploads', nome_arquivo))
        
        f.save(caminho_arquivo)  # Salva o arquivo

        # Recuperar a instância de Sala com base no nome fornecido no formulário
        sala = Sala.get(Sala.nome_sala == data['sala'])

        Upload.create(
            nome_arquivo=nome_arquivo,
            sala=sala,  # Passar a instância de Sala aqui
            data_registro=data['data_registro'],
            hora_registro=data['hora_registro'],
            caminho_arquivo=caminho_arquivo
        )

        return redirect(url_for('home.home'))
    else:
        flash("Arquivo não permitido!")
        return redirect(request.referrer)
    
@upload_route.route('/actions_lista')
def actions_lista():

    """ Renderiza os botões de ação da lista """

    return render_template("actions_lista_upload.html")

@upload_route.route('/new')
def form_upload():

    """ Renderiza o formulário de uploads """
    
    salas = Sala.select()

    return render_template("form_upload.html", salas=salas)

@upload_route.route('/<int:upload_id>/edit')
def form_edit_upload(upload_id):

    """ Renderiza o formulário de uploads para editar um upload existente """

    upload_selecionado = Upload.get_by_id(upload_id)
    salas = Sala.select()

    return render_template("form_upload.html", upload=upload_selecionado, salas=salas)

@upload_route.route('/<int:upload_id>/update', methods=["POST"])
def atualizar_upload(upload_id):
    
    """ Atualiza o upload """
    
    if request.form.get('_method') == 'PUT':
        basepath = os.path.dirname(__file__)
        data = request.form
        f = request.files['file']

        # Obtém o upload a ser atualizado
        upload_editado = Upload.get_by_id(upload_id)
        old_caminho_arquivo = upload_editado.caminho_arquivo
        old_name = upload_editado.nome_arquivo

        # Aplica secure_filename no novo nome do arquivo
        novo_nome_arquivo = secure_filename(data['nome_arquivo'])
        new_caminho_arquivo = os.path.abspath(os.path.join(basepath, os.pardir, 'uploads', novo_nome_arquivo))

        if not f:  # Se não há arquivo novo sendo enviado
            # Se o nome do arquivo mudou, renomeie o arquivo antigo
            if old_name != novo_nome_arquivo:
                new_filename = gerar_nome_unico(os.path.dirname(old_caminho_arquivo), novo_nome_arquivo)
                new_caminho_arquivo = os.path.abspath(os.path.join(basepath, os.pardir, 'uploads', new_filename))
                os.rename(old_caminho_arquivo, new_caminho_arquivo)
                upload_editado.nome_arquivo = new_filename
                upload_editado.caminho_arquivo = new_caminho_arquivo

        elif f:  # Se há um novo arquivo

            # Apaga o arquivo antigo
            if os.path.exists(old_caminho_arquivo):
                os.remove(old_caminho_arquivo)

            new_filename = gerar_nome_unico(os.path.dirname(old_caminho_arquivo), novo_nome_arquivo)
            new_caminho_arquivo = os.path.abspath(os.path.join(basepath, os.pardir, 'uploads', new_filename))
            f.save(new_caminho_arquivo)
            upload_editado.nome_arquivo = new_filename
            upload_editado.caminho_arquivo = new_caminho_arquivo

        # Atualiza os demais campos
        upload_editado.data_registro = data['data_registro']
        upload_editado.hora_registro = data['hora_registro']

        # Recuperar a instância de Sala com base no nome fornecido no formulário
        sala = Sala.get(Sala.nome_sala == data['sala'])
        upload_editado.sala = sala  # Associa a sala ao upload

        upload_editado.save()  # Salva as alterações no banco

        return redirect(url_for('home.home'))


@upload_route.route('/<int:upload_id>/view_on_form')
def reproduzir_video_form(upload_id):

    """ Reproduz o vídeo no formulário """

    upload = Upload.get_by_id(upload_id)
    nome_arquivo = upload.nome_arquivo
    timestamp = int(time.time())  # Adiciona um timestamp como parâmetro de consulta (Isso evita um bug na reprodução do vídeo e não sei o porquê. NÃO REMOVER)

    return render_template('video.html', nome_arquivo=nome_arquivo, timestamp=timestamp)

@upload_route.route('/<int:upload_id>/view')
def reproduzir_video_modal(upload_id):

    """ Reproduz o vídeo no modal """

    upload = Upload.get_by_id(upload_id)
    nome_arquivo = upload.nome_arquivo
    timestamp = int(time.time())  # Adiciona um timestamp como parâmetro de consulta (Isso evita um bug na reprodução do vídeo e não sei o porquê. NÃO REMOVER)

    return render_template('video.html', nome_arquivo=nome_arquivo, timestamp=timestamp, modal=True)

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
    global cancelado

    cancelado = False
    
    basepath = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))
    model_path = os.path.abspath(os.path.join(basepath, 'ai_models', 'best.onnx'))
    upload = Upload.get_by_id(upload_id)
    video_path = os.path.expanduser(upload.caminho_arquivo)

    # Carrega o modelo pré-treinado
    model = YOLO(model_path)
    cap = cv2.VideoCapture(video_path)

    # Função para processar cada frame do vídeo
    def identificar(frame, frame_count):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = model.predict(frame_rgb)[0]  # Obtem apenas o primeiro resultado
        high_conf_boxes = []
        
        # Variáveis para contar as detecções
        qtde_objetos = 0
        qtde_objeto_prestando_atencao = 0
        qtde_objeto_copiando = 0
        qtde_objeto_conversando = 0
        qtde_objeto_distraido = 0
        qtde_objeto_mexendo_celular = 0
        qtde_objeto_dormindo = 0

        if results.boxes:  # Se há detecções
            for box in results.boxes:
                obj_class = box.cls.item()
                conf = box.conf.item()
                if conf >= 0.5:
                    high_conf_boxes.append(box)
                    qtde_objetos += 1

                    # Incrementa as contagens com base na classe do objeto
                    if obj_class == 0:
                        qtde_objeto_prestando_atencao += 1
                    elif obj_class == 1:
                        qtde_objeto_copiando += 1
                    elif obj_class == 2:
                        qtde_objeto_conversando += 1
                    elif obj_class == 3:
                        qtde_objeto_distraido += 1
                    elif obj_class == 4:
                        qtde_objeto_mexendo_celular += 1
                    elif obj_class == 5:
                        qtde_objeto_dormindo += 1

        # Salva a análise no banco de dados
        Analise.create(
            nome_analise=f"Análise do Frame {frame_count}",
            upload=upload,
            qtde_objetos=qtde_objetos,
            qtde_objeto_prestando_atencao=qtde_objeto_prestando_atencao,
            qtde_objeto_copiando=qtde_objeto_copiando,
            qtde_objeto_conversando=qtde_objeto_conversando,
            qtde_objeto_distraido=qtde_objeto_distraido,
            qtde_objeto_mexendo_celular=qtde_objeto_mexendo_celular,
            qtde_objeto_dormindo=qtde_objeto_dormindo
        )

    if not cap.isOpened():
        flash("Erro ao abrir o vídeo!")
        return redirect(request.referrer)

    frame_count = 0
    frame_interval = 1800

    while not cancelado and cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        if frame_count % frame_interval == 0:
            identificar(frame, frame_count)

    cap.release()

    if not cancelado:
        atualizar_status(upload_id)
        flash("Análise concluída!")
    else:
        flash("Análise interrompida pelo usuário.")

    return redirect(url_for('home.home'))


@upload_route.route('<int:upload_id>/cancelar_analise', methods=["POST"])
def cancelar_analise(upload_id):

    global cancelado

    cancelado = True

    deletar_analise(upload_id)

    return redirect(url_for('home.home'))

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