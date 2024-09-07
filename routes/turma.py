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

    return render_template("turma_templates/lista_turmas.html", turmas=turmas)

@turma_route.route('/new')
def form_turma():

    """ Renderiza o formulário de turmas """

    periodos = Periodo.select()
    salas = Sala.select()

    salas_ativas = []

    for sala in salas:
        if (sala.is_ativa == True):
            salas_ativas.append(sala)

    return render_template("turma_templates/form_turma.html", periodos=periodos, salas=salas)

@turma_route.route('/', methods=["POST"])
def inserir_turma():

    """ Adiciona uma turma """

    data = request.form

    # Recuperar a instância de Sala e do Período com base no nome fornecido no formulário
    sala = Sala.get(Sala.nome_sala == data['sala'])
    periodo = Periodo.get(Periodo.nome_periodo == data['periodo'])

    Turma.create(
        nome_turma=data['nome_turma'],
        sala=sala,
        periodo=periodo,
        qtde_alunos=data['qtde_alunos']
    )

    return redirect(url_for('home.home'))

@turma_route.route('<int:turma_id>/edit')
def form_edit_turma(turma_id):

    periodos = Periodo.select()
    salas = Sala.select()

    turma_selecionada = Turma.get_by_id(turma_id)

    return render_template("turma_templates/form_turma.html", turma=turma_selecionada, periodos=periodos, salas=salas)

@turma_route.route('/<int:turma_id>/update', methods=["POST"])
def atualizar_turma(turma_id):
    if request.form.get('_method') == "PUT":
        data = request.form

        turma_editada = Turma.get_by_id(turma_id)

        # Recuperar a instância de Sala com base no nome fornecido no formulário
        sala = Sala.get(Sala.nome_sala == data['sala'])

        # Recuperar a instância do Período com base no nome fornecido no formulário
        periodo = Periodo.get(Periodo.nome_periodo == data['periodo'])

        turma_editada.nome_turma = data['nome_turma']
        turma_editada.sala = sala
        turma_editada.periodo = periodo
        turma_editada.qtde_alunos = data['qtde_alunos']

        turma_editada.save()

    return redirect(url_for('home.home'))

@turma_route.route('<int:turma_id>/delete', methods=["DELETE"])
def deletar_turma(turma_id):

    """ Deleta o registro da turma selecionada """

    turma = Turma.get_by_id(turma_id)

    turma.delete_instance()

    return {"deleted": "ok"}
