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