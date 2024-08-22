import os, time
from flask import Blueprint, url_for, render_template, redirect, send_from_directory, flash, session, request
from werkzeug.utils import secure_filename
from database.models.upload import Upload
from database.models.turma import Turma
from funcoes_extras import alterando_sessions_para_false

upload_route = Blueprint("upload", __name__)

UPLOAD_FOLDER = os.path.abspath(os.path.join(os.getcwd(), os.pardir, 'uploads'))
ALLOWED_EXTENSIONS = {'asf', 'avi', 'm4v', 'mkv', 'mov', 'mp4', 'mpeg', 'mpg', 'ts', 'wmv', 'webm'}

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

    has_nao_analisado = any(upload.is_analisado == 0 for upload in uploads_nao_analisados) # Passa como parâmetro se é upload analisado ou não, para renderizar o conteúdo da maneira correta
    
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

    """ Insere um upload """
    f = request.files['file']

    if f and allowed_file(f.filename):
        basepath = os.path.dirname(__file__)
        data = request.form

        # Substituir espaços por underlines
        nome_arquivo = data['nome_arquivo'].replace(' ', '_')

        # Usa o nome fornecido pelo usuário no formulário
        filename = secure_filename(data['nome_arquivo'])
        old_caminho_arquivo = os.path.abspath(os.path.join(basepath, os.pardir, 'uploads', filename))

        base, extension = os.path.splitext(filename) # Separa o nome do arquivo da sua extensão (usa-se isso para remover acentos e caracteres especias que podem comprometer o registro do arquivo)

        nome_arquivo = f"{base}{extension}" # Renomeia o arquivo com os caracteres especiais substituídos

        nome_arquivo = gerar_nome_unico(os.path.dirname(old_caminho_arquivo), nome_arquivo) # Cria um nome único para evitar conflitos

        caminho_arquivo = os.path.abspath(os.path.join(basepath, os.pardir, 'uploads', nome_arquivo))
        
        f.save(caminho_arquivo) # Salva o arquivo

        Upload.create(
            nome_arquivo = nome_arquivo,
            turma = data['turma'],
            data_registro = data['data_registro'],
            hora_registro = data['hora_registro'],
            caminho_arquivo = caminho_arquivo
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
    
    turmas = Turma.select()

    return render_template("form_upload.html", turmas=turmas)

@upload_route.route('/<int:upload_id>/edit')
def form_edit_upload(upload_id):

    """ Renderiza o formulário de uploads para editar um upload existente """

    upload_selecionado = Upload.get_by_id(upload_id)
    turmas = Turma.select()

    return render_template("form_upload.html", upload=upload_selecionado, turmas=turmas)

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
        upload_editado.turma = data['turma']
        upload_editado.data_registro = data['data_registro']
        upload_editado.hora_registro = data['hora_registro']

        upload_editado.save()  # Salva o novo registro no banco

        return redirect(url_for('home.home'))

@upload_route.route('/<int:upload_id>/view')
def reproduzir_video(upload_id):

    """ Reproduz o vídeo """

    upload = Upload.get_by_id(upload_id)
    nome_arquivo = upload.nome_arquivo
    timestamp = int(time.time())  # Adiciona um timestamp como parâmetro de consulta (Isso evita um bug na reprodução do vídeo e não sei o porquê. NÃO REMOVER)

    return render_template('video.html', nome_arquivo=nome_arquivo, timestamp=timestamp)

@upload_route.route('/<filename>')
def uploaded_file(filename):

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
