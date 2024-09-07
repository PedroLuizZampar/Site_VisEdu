from flask import Blueprint, url_for, render_template, redirect, flash, session, request
from database.models.sala import Sala
from funcoes_extras import alterando_sessions_para_false

sala_route = Blueprint("sala", __name__)


@sala_route.route('/')
def lista_salas():

    salas = Sala.select()

    salas_ativas = []

    for sala in salas:
        if (sala.is_ativa == True):
            salas_ativas.append(sala)

    alterando_sessions_para_false()
    session['visualizando_salas'] = True

    return render_template("sala_templates/lista_salas.html", salas=salas_ativas)

@sala_route.route('/new')
def form_sala():

    return render_template("sala_templates/form_sala.html")

@sala_route.route('/', methods=["POST"])
def inserir_sala():
    data = request.form

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

        sala_editada = Sala.get_by_id(sala_id)

        sala_editada.nome_sala = data['nome_sala']

        sala_editada.save()

    return redirect(url_for('home.home'))

@sala_route.route('/<int:sala_id>/delete', methods=["DELETE"])
def deletar_sala(sala_id):

    sala = Sala.get_by_id(sala_id)

    sala.is_ativa = False

    sala.save()

    return {"Sala inativada": "ok"}