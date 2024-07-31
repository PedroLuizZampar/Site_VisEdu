from flask import Blueprint, render_template, request
from database.upload import UPLOADS

upload_route = Blueprint("upload", __name__)

@upload_route.route('/')
def lista_uploads():

    """ Renderiza a lista de uploads """

    return render_template("lista_uploads.html", uploads=UPLOADS)

@upload_route.route('/', methods=["POST"])
def inserir_upload():

    """ Insere um upload """

    data = request.json

    novo_upload = {
        "id": len(UPLOADS) + 1,
        "nome_arquivo": data['nome_arquivo'],
        "turma": data['turma'],
        "data_registro": data['data_registro'],
        "hora_registro": data['hora_registro']
    }

    UPLOADS.append(novo_upload)

    return render_template('item_upload.html', upload=novo_upload)

@upload_route.route('new')
def form_upload():

    """ Renderiza o formulário de uploads """

    return render_template("form_upload.html")

@upload_route.route('/<int:upload_id>/edit')
def form_edit_upload(upload_id):
    """ Renderiza o formulário de uploads para editar um upload existente """

    upload_selecionado = None

    for u in UPLOADS:
        if u['id'] == upload_id:
            upload_selecionado = u

    return render_template("form_upload.html", upload=upload_selecionado)

@upload_route.route('/<int:upload_id>/update', methods=["PUT"])
def atualizar_upload(upload_id):
    """ Atualiza o upload com os novos dados informados no formulário """

    upload_editado = None

    data = request.json
    for u in UPLOADS:
        if u['id'] == upload_id:
            u['nome_arquivo'] = data['nome_arquivo']
            u['turma'] = data['turma']
            u['data_registro'] = data['data_registro']
            u['hora_registro'] = data['hora_registro']

            upload_editado = u
    
    return render_template('item_upload.html', upload=upload_editado)

@upload_route.route('/<int:upload_id>/delete', methods=["DELETE"])
def deletar_upload(upload_id):

    """ Apaga um upload do sistema """

    global UPLOADS
    UPLOADS = [u for u in UPLOADS if u['id'] != upload_id]

    return {"deleted": "ok"}