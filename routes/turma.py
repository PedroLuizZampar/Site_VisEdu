from flask import Blueprint, url_for, render_template, redirect, session, request
from database.models.turma import Turma
from database.models.sala import Sala
from database.models.periodo import Periodo
from funcoes_extras import alterando_sessions_para_false

turma_route = Blueprint("turma", __name__)

@turma_route.route('/')
def lista_turmas():

    """ Renderiza as turmas """

    turmas = Turma.select()

    alterando_sessions_para_false()
    session['visualizando_turmas'] = True

    return render_template("lista_turmas.html", turmas=turmas)

@turma_route.route('/new')
def form_turma():

    """ Renderiza o formulário de turmas """

    return render_template("form_turmas.html")

@turma_route.route('/', methods=["POST"])
def inserir_turma():

    """ Adiciona uma turma """

    data = request.form

    # Recuperar a instância de Sala e do Período com base no nome fornecido no formulário
    sala = Sala.get(Sala.nome_sala == data['sala'])
    periodo = Sala.get(Periodo.nome_periodo == data['periodo'])

    Turma.create(
        nome_turma=data['nome_turma'],
        sala=sala,
        periodo=periodo,
        qtde_alunos=data['qtde_alunos']
    )

@turma_route.route('<int:turma_id>/delete', methods=["DELETE"])
def deletar_turma(turma_id):

    """ Deleta o registro da turma selecionada """

    turma = Turma.get_by_id(turma_id)

    turma.delete_instance()

    return {"deleted": "ok"}
