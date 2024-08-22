from flask import Blueprint, url_for, render_template, redirect, flash, session, request
from database.models.turma import Turma
from funcoes_extras import alterando_sessions_para_false

turma_route = Blueprint("turma", __name__)


@turma_route.route('/')
def lista_turmas():

    turmas = Turma.select()

    alterando_sessions_para_false()
    session['visualizando_turmas'] = True

    return render_template("lista_turmas.html", turmas=turmas)

@turma_route.route('/actions_lista')
def actions_lista():

    return render_template("actions_lista_turma.html")

@turma_route.route('/new')
def form_turma():

    return render_template("form_turma.html")

@turma_route.route('/', methods=["POST"])
def inserir_turma():
    data = request.form

    Turma.create(
        nome_turma=data['nome_turma']
    )

    # Armazena dados temporariamente na sessão
    session['visualizando_turmas'] = True

    return redirect(url_for('home.home'))

@turma_route.route('<int:turma_id>/edit')
def form_edit_turma(turma_id):

    turma_selecionada = Turma.get_by_id(turma_id)

    return render_template("form_turma.html", turma=turma_selecionada)

@turma_route.route('/<int:turma_id>/update', methods=["POST"])
def atualizar_turma(turma_id):
    if request.form.get('_method') == "PUT":
        data = request.form

        turma_editada = Turma.get_by_id(turma_id)

        turma_editada.nome_turma = data['nome_turma']

        turma_editada.save()

    return redirect(url_for('home.home'))

@turma_route.route('/<int:turma_id>/delete', methods=["DELETE"])
def deletar_turma(turma_id):

    turma = Turma.get_by_id(turma_id)

    turma.delete_instance()

    return {"deleted": "ok"}