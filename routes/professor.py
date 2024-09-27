from datetime import datetime
from flask import Blueprint, url_for, render_template, redirect, flash, session, request
from database.models.professor import Professor
from database.models.disciplina import Disciplina
from database.models.aula import Aula
from database.models.turma import Turma
from funcoes_extras import alterando_sessions_para_false

professor_route = Blueprint("professor", __name__)

@professor_route.route('/lista_professores')
def lista_professores():
    professores = Professor.select()

    alterando_sessions_para_false()
    session['visualizando_professores'] = True
    
    return render_template("cadastro/professor_templates/lista_professores.html", professores=professores)

@professor_route.route('/lista_aulas_professor_matutino')
def lista_aulas_professor_matutino():
    aulas = Aula.select().where(Aula.periodo == 1)
    turmas = Turma.select().where(Turma.periodo == 1)
    
    return render_template("cadastro/professor_templates/lista_aulas_professor_matutino.html", aulas=aulas, turmas=turmas)

@professor_route.route('/lista_aulas_professor_vespertino')
def lista_aulas_professor_vespertino():
    aulas = Aula.select().where(Aula.periodo == 2)
    turmas = Turma.select().where(Turma.periodo == 2)
    
    return render_template("cadastro/professor_templates/lista_aulas_professor_vespertino.html", aulas=aulas, turmas=turmas)

@professor_route.route('/lista_aulas_professor_noturno')
def lista_aulas_professor_noturno():
    aulas = Aula.select().where(Aula.periodo == 3)
    turmas = Turma.select().where(Turma.periodo == 3)
    
    return render_template("cadastro/professor_templates/lista_aulas_professor_noturno.html", aulas=aulas, turmas=turmas)

@professor_route.route('/new')
def form_professor():

    disciplinas = Disciplina.select()
    aulas_matutinas = Aula.select().where(Aula.id == 1)
    aulas_vespertinas = Aula.select().where(Aula.id == 2)
    aulas_noturnas = Aula.select().where(Aula.id == 3)

    return render_template("cadastro/professor_templates/form_professor.html", disciplinas=disciplinas, aulas_matutinas=aulas_matutinas, aulas_vespertinas=aulas_vespertinas, aulas_noturnas=aulas_noturnas)

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