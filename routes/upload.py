import os
import re
from flask import Blueprint, url_for, render_template, redirect, send_from_directory, request
from werkzeug.utils import secure_filename
from database.models.upload import Upload

upload_route = Blueprint("upload", __name__)

UPLOAD_FOLDER = os.path.abspath(os.path.join(os.getcwd(), os.pardir, 'uploads'))
ALLOWED_EXTENSIONS = {'asf', 'avi', 'm4v', 'mkv', 'mov', 'mp4', 'mpeg', 'mpg', 'ts', 'wmv', 'webm'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@upload_route.route('/')
def lista_uploads():

    """ Renderiza a lista de uploads """

    uploads = Upload.select()
    return render_template("lista_uploads.html", uploads=uploads)

@upload_route.route('/', methods=["POST"])
def inserir_upload():

    """ Insere um upload """
    f = request.files['file']

    if f.filename == '':
        return "Nenhum arquivo selecionado!"

    if f and allowed_file(f.filename):
        basepath = os.path.dirname(__file__)
        data = request.form

        # Substituir espaços por underlines
        nome_arquivo = data['nome_arquivo'].replace(' ', '_')

        if not re.match(r'^[a-zA-Z0-9_]+$', nome_arquivo):
            return "O nome do arquivo só pode conter letras, números e underlines!"
        
        # Usa o nome fornecido pelo usuário no formulário
        filename = secure_filename(data['nome_arquivo'])
        caminho_arquivo = os.path.abspath(os.path.join(basepath, os.pardir, 'uploads', filename))
        
        f.save(caminho_arquivo)

        Upload.create(
            nome_arquivo = nome_arquivo,
            turma = data['turma'],
            data_registro = data['data_registro'],
            hora_registro = data['hora_registro'],
            caminho_arquivo = caminho_arquivo
        )

        return redirect(url_for('home.home'))
    else:
        return "Arquivo não permitido!"

@upload_route.route('/new')
def form_upload():

    """ Renderiza o formulário de uploads """

    return render_template("form_upload.html")

@upload_route.route('/<int:upload_id>/edit')
def form_edit_upload(upload_id):

    """ Renderiza o formulário de uploads para editar um upload existente """

    upload_selecionado = Upload.get_by_id(upload_id)

    return render_template("form_upload.html", upload=upload_selecionado)

@upload_route.route('/<int:upload_id>/update', methods=["POST"])
def atualizar_upload(upload_id):

    """ Atualiza o upload """

    if request.form.get('_method') == 'PUT': # Transforma a requisição em um método PUT
        
        basepath = os.path.dirname(__file__)
        
        data = request.form
        f = request.files['file']

        filename = secure_filename(data['nome_arquivo'])
        caminho_arquivo = os.path.abspath(os.path.join(basepath, os.pardir, 'uploads', filename)) # Cria o caminho relativo para salvar o arquivo na pasta uploads com o nome informado no formulário

        upload_editado = Upload.get_by_id(upload_id)

        upload_editado.nome_arquivo = data['nome_arquivo']
        upload_editado.turma = data['turma']
        upload_editado.data_registro = data['data_registro']
        upload_editado.hora_registro = data['hora_registro']
        upload_editado.caminho_arquivo = caminho_arquivo

        os.remove(Upload.get_by_id(upload_id).caminho_arquivo) # Apaga o arquivo antigo
        
        f.save(caminho_arquivo) # Salva o novo upload no servidor
        upload_editado.save() # Salva o novo registro no banco

        return redirect(url_for('home.home'))

@upload_route.route('/<int:upload_id>/view')
def reproduzir_video (upload_id):

    """ Reproduz o vídeo """

    upload = Upload.get_by_id(upload_id)
    nome_arquivo = upload.nome_arquivo

    return render_template('video.html', nome_arquivo=nome_arquivo)

@upload_route.route('/uploads/<filename>')
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