from datetime import datetime
from flask import Blueprint, url_for, render_template, redirect, flash, session, request
from database.models.professor import Professor
from database.models.disciplina import Disciplina
from database.models.aula import Aula
from database.models.periodo import Periodo
from database.models.turma import Turma
from funcoes_extras import alterando_sessions_para_false

professor_route = Blueprint("professor", __name__)

@professor_route.route('/lista_professores_matutinos')
def lista_professores_matutinos():
    periodo = Periodo.select().where(Periodo.nome_periodo == "Matutino")
    professores = Professor.select().where(Professor.periodo == 1)

    alterando_sessions_para_false()
    session['visualizando_professores'] = True
    session['visualizando_professores_matutinos'] = True
    
    return render_template("cadastro/professor_templates/lista_professores_matutinos.html", professores=professores, periodo=periodo)

@professor_route.route('/lista_professores_vespertinos')
def lista_professores_vespertinos():
    periodo = Periodo.select().where(Periodo.nome_periodo == "Vespertino")
    professores = Professor.select().where(Professor.periodo == 2)

    alterando_sessions_para_false()
    session['visualizando_professores'] = True
    session['visualizando_professores_vespertinos'] = True
    
    return render_template("cadastro/professor_templates/lista_professores_vespertinos.html", professores=professores, periodo=periodo)

@professor_route.route('/lista_professores_noturnos')
def lista_professores_noturnos():
    periodo = Periodo.select().where(Periodo.nome_periodo == "Noturno")
    professores = Professor.select().where(Professor.periodo == 3)

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
    if periodo_id == 1:
        periodo = Periodo.select().where(Periodo.nome_periodo == "Matutino")
    elif periodo_id == 2:
        periodo = Periodo.select().where(Periodo.nome_periodo == "Vespertino")
    if periodo_id == 3:
        periodo = Periodo.select().where(Periodo.nome_periodo == "Noturno")

    professores = Professor.select()
    aulas = Aula.select().where(Aula.periodo == periodo)
    turmas = Turma.select().where(Turma.periodo == periodo)
    
    return render_template("cadastro/professor_templates/lista_aulas_professor.html", professores=professores, aulas=aulas, turmas=turmas)

@professor_route.route('/', methods=["POST"])
def inserir_professor():
    data = request.form

    # Cria a professor com os dados fornecidos
    Professor.create(
        
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

    professor = professor.get_by_id(professor_id)

    professor.delete_instance()

    return {"professor excluído": "ok"}