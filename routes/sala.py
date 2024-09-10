from flask import Blueprint, url_for, render_template, redirect, flash, session, request
from database.models.sala import Sala
from database.models.upload import Upload
from database.models.turma import Turma
from funcoes_extras import alterando_sessions_para_false

sala_route = Blueprint("sala", __name__)


@sala_route.route('/')
def lista_salas():

    salas = Sala.select()

    alterando_sessions_para_false()
    session['visualizando_salas'] = True

    return render_template("sala_templates/lista_salas.html", salas=salas)

@sala_route.route('/new')
def form_sala():

    return render_template("sala_templates/form_sala.html")

@sala_route.route('/', methods=["POST"])
def inserir_sala():
    data = request.form

    sala_existente_nome = Sala.select().where(Sala.nome_sala == data['nome_sala']).first()

    if sala_existente_nome:
        flash("Já existe uma sala cadastrada com esse nome!", "error")
        return redirect(url_for('home.home'))

    Sala.create(
        nome_sala=data['nome_sala']
    )

    # Armazena dados temporariamente na sessão
    session['visualizando_salas'] = True

    return redirect(url_for('home.home'))

@sala_route.route('<int:sala_id>/edit')
def form_edit_sala(sala_id):

    sala_selecionada = Sala.get_by_id(sala_id)

    return render_template("sala_templates/form_sala.html", sala=sala_selecionada)

@sala_route.route('/<int:sala_id>/update', methods=["POST"])
def atualizar_sala(sala_id):
    if request.form.get('_method') == "PUT":
        data = request.form

        sala_existente_nome = Sala.select().where(
            (Sala.nome_sala == data['nome_sala']) & (Sala.id != sala_id)
            ).first()
        
        if sala_existente_nome:
            flash("Já existe uma sala cadastrada com esse nome!", "error")
            return redirect(url_for('home.home'))

        sala_editada = Sala.get_by_id(sala_id)

        sala_editada.nome_sala = data['nome_sala']

        sala_editada.save()

    return redirect(url_for('home.home'))

@sala_route.route('/<int:sala_id>/delete', methods=["DELETE"])
def deletar_sala(sala_id):

    sala = Sala.get_by_id(sala_id)
    uploads = Upload.select()
    turmas = Turma.select()

    for upload in uploads:
        if upload.sala == sala:
            upload.sala = None
            upload.save()

    for turma in turmas:
        if turma.sala == sala:
            turma.sala = None
            turma.save()

    sala.delete_instance()

    return {"Sala excluída": "ok"}