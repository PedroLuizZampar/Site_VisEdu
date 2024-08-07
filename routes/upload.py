import os
from flask import Blueprint, url_for, render_template, redirect, flash, request
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
        
        # Usa o nome fornecido pelo usuário no formulário
        filename = secure_filename(data['nome_arquivo'])
        filepath = os.path.abspath(os.path.join(basepath, os.pardir, 'uploads', filename))
        
        f.save(filepath)

        Upload.create(
            nome_arquivo = data['nome_arquivo'],
            turma = data['turma'],
            data_registro = data['data_registro'],
            hora_registro = data['hora_registro'],
            caminho_arquivo = filepath
        )

        return redirect(url_for('home.home'))
    else:
        return "Arquivo não permitido!"

@upload_route.route('new')
def form_upload():

    """ Renderiza o formulário de uploads """

    return render_template("form_upload.html")

@upload_route.route('/<int:upload_id>/edit')
def form_edit_upload(upload_id):

    """ Renderiza o formulário de uploads para editar um upload existente """

    upload_selecionado = Upload.get_by_id(upload_id)

    return render_template("form_upload.html", upload=upload_selecionado)

@upload_route.route('/<int:upload_id>/update', methods=["PUT"])
def atualizar_upload(upload_id):

    """ Atualiza o upload com os novos dados informados no formulário """

    data = request.json
    
    upload_editado = Upload.get_by_id(upload_id)

    upload_editado.nome_arquivo = data['nome_arquivo']
    upload_editado.turma = data['turma']
    upload_editado.data_registro = data['data_registro']
    upload_editado.hora_registro = data['hora_registro']

    upload_editado.save() # Salva, no banco de dados, o registro feito através do formulário de edição

    return render_template('item_upload.html', upload=upload_editado)

@upload_route.route('/<int:upload_id>/delete', methods=["DELETE"])
def deletar_upload(upload_id):

    """ Apaga um upload do sistema """

    upload = Upload.get_by_id(upload_id) # Quando estamos passando o valor de uma classe para uma variável, estamos instanciando ela
    upload.delete_instance() # Aqui deletamos a instância

    return {"deleted": "ok"}