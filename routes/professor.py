from datetime import datetime
from flask import Blueprint, url_for, render_template, redirect, flash, session, request
from database.models.professor import Professor
from database.models.aula_professor import Aula_Professor
from database.models.disciplina import Disciplina
from database.models.aula import Aula
from database.models.periodo import Periodo
from database.models.turma import Turma
from funcoes_extras import alterando_sessions_para_false

professor_route = Blueprint("professor", __name__)

@professor_route.route('/lista_professores_matutinos')
def lista_professores_matutinos():
    periodo = Periodo.select().where(Periodo.nome_periodo == "Matutino")
    professores = Professor.select().where(Professor.periodo == periodo)

    alterando_sessions_para_false()
    session['visualizando_professores'] = True
    session['visualizando_professores_matutinos'] = True
    
    return render_template("cadastro/professor_templates/lista_professores_matutinos.html", professores=professores, periodo=periodo)

@professor_route.route('/lista_professores_vespertinos')
def lista_professores_vespertinos():
    periodo = Periodo.select().where(Periodo.nome_periodo == "Vespertino")
    professores = Professor.select().where(Professor.periodo == periodo)

    alterando_sessions_para_false()
    session['visualizando_professores'] = True
    session['visualizando_professores_vespertinos'] = True
    
    return render_template("cadastro/professor_templates/lista_professores_vespertinos.html", professores=professores, periodo=periodo)

@professor_route.route('/lista_professores_noturnos')
def lista_professores_noturnos():
    periodo = Periodo.select().where(Periodo.nome_periodo == "Noturno")
    professores = Professor.select().where(Professor.periodo == periodo)

    alterando_sessions_para_false()
    session['visualizando_professores'] = True
    session['visualizando_professores_noturnos'] = True
    
    return render_template("cadastro/professor_templates/lista_professores_noturnos.html", professores=professores, periodo=periodo)

@professor_route.route('periodo-<int:periodo_id>/new')
def form_professor(periodo_id):
    id_periodo=periodo_id

    disciplinas = Disciplina.select()

    return render_template("cadastro/professor_templates/form_professor.html", disciplinas=disciplinas, id_periodo=id_periodo)

@professor_route.route('periodo-<int:periodo_id>/lista_aulas_professor')
def lista_aulas_professor(periodo_id):

    professores = Professor.select()
    aulas = Aula.select().where(Aula.periodo_id == periodo_id)
    turmas = Turma.select().where(Turma.periodo_id == periodo_id)
    
    return render_template("cadastro/professor_templates/lista_aulas_professor.html", professores=professores, aulas=aulas, turmas=turmas)

@professor_route.route('periodo-<int:periodo_id>/', methods=["POST"])
def inserir_professor(periodo_id):
    data = request.form

    if periodo_id == 1:
        periodo = Periodo.select().where(Periodo.nome_periodo == "Matutino")
    elif periodo_id == 2:
        periodo = Periodo.select().where(Periodo.nome_periodo == "Vespertino")
    if periodo_id == 3:
        periodo = Periodo.select().where(Periodo.nome_periodo == "Noturno")

    # Cria a professor com os dados fornecidos
    professor_novo = Professor.create(
        nome_professor = data["nome_professor"],
        periodo = periodo,
        disciplina = Disciplina.select().where(Disciplina.nome_disciplina ==data["disciplina"]),
        email = data["email"]
    )

    aulas_periodo = Aula.select().where(Aula.periodo == periodo)

    cont = 1
    for aula in aulas_periodo:
        aulas_dados = []

        aula_seg = Turma.select().where(Turma.nome_turma == data[f"seg-{cont}"])
        aula_ter = Turma.select().where(Turma.nome_turma == data[f"ter-{cont}"])
        aula_qua = Turma.select().where(Turma.nome_turma == data[f"qua-{cont}"])
        aula_qui = Turma.select().where(Turma.nome_turma == data[f"qui-{cont}"])
        aula_sex = Turma.select().where(Turma.nome_turma == data[f"sex-{cont}"])

        cont += 1

        aulas_dados.extend([aula_seg, aula_ter, aula_qua, aula_qui, aula_sex])

        for aula_dado in aulas_dados:
            if aula_dado:
                Aula_Professor.create(
                    turma = aula_dado,
                    professor = professor_novo.id,
                    aula = aula.id
                )

    # Armazena dados temporariamente na sessão
    session['visualizando_professores'] = True

    return redirect(url_for('cadastro.tela_cadastro'))

@professor_route.route('<int:professor_id>/edit')
def form_edit_professor(professor_id):

    professor_selecionado = Professor.get_by_id(professor_id)

    disciplinas = Disciplina.select()

    return render_template("cadastro/professor_templates/form_professor.html", professor=professor_selecionado, disciplinas=disciplinas)

@professor_route.route('/<int:professor_id>/update', methods=["POST"])
def atualizar_professor(professor_id):
    if request.form.get('_method') == "PUT":
        data = request.form

    return redirect(url_for('cadastro.tela_cadastro'))

@professor_route.route('/<int:professor_id>/delete', methods=["DELETE"])
def deletar_professor(professor_id):

    aulas_professor = Aula_Professor.select().where(Aula_Professor.professor_id == professor_id)
    professor = Professor.get_by_id(professor_id)

    for aula in aulas_professor:
        aula.delete_instance()

    professor.delete_instance()

    return {"professor excluído": "ok"}