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
    turmas = Turma.select().where(Turma.periodo == periodo_id)
    aulas = Aula.select().where(Aula.periodo == periodo_id)

    return render_template("cadastro/professor_templates/form_professor.html", disciplinas=disciplinas, id_periodo=id_periodo, turmas=turmas, aulas=aulas)

@professor_route.route('periodo-<int:periodo_id>/lista_aulas_professor')
def lista_aulas_professor(periodo_id):

    professores = Professor.select()
    aulas = Aula.select().where(Aula.periodo_id == periodo_id)
    turmas = Turma.select().where(Turma.periodo_id == periodo_id)
    
    return render_template("cadastro/professor_templates/lista_aulas_professor.html", professores=professores, aulas=aulas, turmas=turmas)

@professor_route.route('periodo-<int:periodo_id>/', methods=["POST"])
def inserir_professor(periodo_id):
    data = request.form

    # Determina o período com base no ID
    periodo = Periodo.get_by_id(periodo_id)

    # Validação 1: Verifica se o nome do professor já existe no mesmo período
    professor_existente = Professor.select().where(
        (Professor.nome_professor == data["nome_professor"]) &
        (Professor.periodo == periodo)
    ).first()

    if professor_existente:
        flash('Já existe um professor com esse nome no mesmo período!', "error")
        return redirect(url_for('cadastro.tela_cadastro'))

    # Cria o novo professor
    disciplina = Disciplina.get(Disciplina.nome_disciplina == data["disciplina"])
    professor_novo = Professor.create(
        nome_professor=data["nome_professor"],
        periodo=periodo,
        disciplina=disciplina,
        email=data["email"]
    )

    aulas_periodo = Aula.select().where(Aula.periodo == periodo)

    conflict_messages = []
    i = 1
    for aula in aulas_periodo:
        # Obter os IDs das turmas selecionadas para cada dia
        aula_seg_id = data.get(f"seg-{i}")
        aula_ter_id = data.get(f"ter-{i}")
        aula_qua_id = data.get(f"qua-{i}")
        aula_qui_id = data.get(f"qui-{i}")
        aula_sex_id = data.get(f"sex-{i}")

        dias_semana = ['segunda-feira', 'terça-feira', 'quarta-feira', 'quinta-feira', 'sexta-feira']
        turma_ids = [aula_seg_id, aula_ter_id, aula_qua_id, aula_qui_id, aula_sex_id]

        for dia_semana, turma_id in zip(dias_semana, turma_ids):
            if turma_id:
                turma = Turma.get_by_id(int(turma_id))

                # Verifica se a turma já está vinculada à mesma aula e dia da semana para outro professor no mesmo período
                aula_professor_existente = Aula_Professor.select().join(Professor).where(
                    (Aula_Professor.turma == turma) &
                    (Aula_Professor.aula == aula) &
                    (Aula_Professor.dia_semana == dia_semana) &
                    (Professor.periodo == periodo)
                ).first()

                if aula_professor_existente:
                    # Obter o nome do professor que possui a aula conflitante
                    professor_conflitante = aula_professor_existente.professor.nome_professor
                    conflict_messages.append(
                        f"A turma {turma.nome_turma} já está vinculada à {i}ª aula de {dia_semana} para o professor {professor_conflitante} no mesmo período!"
                    )
                    continue  # Pula esta aula e continua com a próxima
                else:
                    # Cria a relação Aula_Professor
                    Aula_Professor.create(
                        turma=turma,
                        professor=professor_novo,
                        aula=aula,
                        dia_semana=dia_semana
                    )
        i += 1

    # Após processar todas as aulas, exibe as mensagens de conflito
    if conflict_messages:
        for msg in conflict_messages:
            flash(msg, "error")

    # Armazena dados temporariamente na sessão
    session['visualizando_professores'] = True

    return redirect(url_for('cadastro.tela_cadastro'))

@professor_route.route('periodo-<int:periodo_id>/professor-<int:professor_id>/edit')
def form_edit_professor(periodo_id, professor_id):
    id_periodo = periodo_id

    professor_selecionado = Professor.get_by_id(professor_id)
    disciplinas = Disciplina.select()
    aulas = Aula.select().where(Aula.periodo == periodo_id)
    turmas = Turma.select().where(Turma.periodo == periodo_id)

    # Obter as aulas associadas ao professor
    aulas_professor = Aula_Professor.select().where(Aula_Professor.professor == professor_selecionado)

    # Organizar o horário em um dicionário: {(aula_id, dia_semana): turma_id}
    horario_professor = {}
    for aula_prof in aulas_professor:
        chave = (aula_prof.aula.id, aula_prof.dia_semana)
        if aula_prof.turma is not None:
            horario_professor[chave] = aula_prof.turma.id
        else:
            horario_professor[chave] = None  # Ou qualquer valor que represente a ausência de uma turma


    return render_template(
        "cadastro/professor_templates/form_professor.html",
        professor=professor_selecionado,
        disciplinas=disciplinas,
        id_periodo=id_periodo,
        aulas=aulas,
        turmas=turmas,
        horario_professor=horario_professor  # Passa o horário para o template
    )

@professor_route.route('/<int:professor_id>/update', methods=["POST"])
def atualizar_professor(professor_id):
    if request.form.get('_method') == "PUT":
        data = request.form

        # Recuperar o professor a ser editado
        professor_editado = Professor.get_by_id(professor_id)

        # Determina o período com base no professor
        periodo = professor_editado.periodo

        # Validação 1: Verifica se já existe outro professor com o mesmo nome no mesmo período (excluindo o atual)
        professor_existente = Professor.select().where(
            (Professor.nome_professor == data["nome_professor"]) &
            (Professor.periodo == periodo) &
            (Professor.id != professor_id)
        ).first()

        if professor_existente:
            flash('Já existe um professor com esse nome no mesmo período!', "error")
            return redirect(url_for('cadastro.tela_cadastro'))

        # Atualizar os campos do professor
        professor_editado.nome_professor = data['nome_professor']
        professor_editado.disciplina = Disciplina.get(Disciplina.nome_disciplina == data["disciplina"])
        professor_editado.email = data['email']
        professor_editado.save()

        aulas_periodo = Aula.select().where(Aula.periodo == periodo)

        conflict_messages = []
        i = 1
        for aula in aulas_periodo:
            # Obter os IDs das turmas selecionadas para cada dia
            aula_seg_id = data.get(f"seg-{i}")
            aula_ter_id = data.get(f"ter-{i}")
            aula_qua_id = data.get(f"qua-{i}")
            aula_qui_id = data.get(f"qui-{i}")
            aula_sex_id = data.get(f"sex-{i}")

            dias_semana = ['segunda-feira', 'terça-feira', 'quarta-feira', 'quinta-feira', 'sexta-feira']
            turma_ids = [aula_seg_id, aula_ter_id, aula_qua_id, aula_qui_id, aula_sex_id]

            for dia_semana, turma_id in zip(dias_semana, turma_ids):
                # Primeiro, deletar a relação existente para esta aula e dia
                Aula_Professor.delete().where(
                    (Aula_Professor.professor == professor_editado) &
                    (Aula_Professor.aula == aula) &
                    (Aula_Professor.dia_semana == dia_semana)
                ).execute()

                if turma_id:
                    turma = Turma.get_by_id(int(turma_id))

                    # Verifica se a turma já está vinculada à mesma aula e dia da semana para outro professor no mesmo período
                    aula_professor_existente = Aula_Professor.select().join(Professor).where(
                        (Aula_Professor.turma == turma) &
                        (Aula_Professor.aula == aula) &
                        (Aula_Professor.dia_semana == dia_semana) &
                        (Professor.periodo == periodo) &
                        (Professor.id != professor_id)
                    ).first()

                    if aula_professor_existente:
                        # Obter o nome do professor que possui a aula conflitante
                        professor_conflitante = aula_professor_existente.professor.nome_professor
                        conflict_messages.append(
                            f"A turma {turma.nome_turma} já está vinculada à {i}ª aula de {dia_semana} para o professor {professor_conflitante} no mesmo período!"
                        )
                        continue  # Pula esta aula e continua com a próxima
                    else:
                        # Cria a relação Aula_Professor
                        Aula_Professor.create(
                            turma=turma,
                            professor=professor_editado,
                            aula=aula,
                            dia_semana=dia_semana
                        )
            i += 1

        # Após processar todas as aulas, exibe as mensagens de conflito
        if conflict_messages:
            for msg in conflict_messages:
                flash(msg, "error")

        return redirect(url_for('cadastro.tela_cadastro'))

@professor_route.route('/<int:professor_id>/delete', methods=["DELETE"])
def deletar_professor(professor_id):

    aulas_professor = Aula_Professor.select().where(Aula_Professor.professor_id == professor_id)
    professor = Professor.get_by_id(professor_id)

    for aula in aulas_professor:
        aula.delete_instance()

    professor.delete_instance()

    return {"professor excluído": "ok"}
