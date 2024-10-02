from datetime import datetime
from flask import Blueprint, url_for, render_template, redirect, flash, session, request
from database.models.aula import Aula
from database.models.upload import Upload
from database.models.turma import Turma
from database.models.periodo import Periodo
from funcoes_extras import alterando_sessions_para_false

aula_route = Blueprint("aula", __name__)

@aula_route.route('/lista_aulas_matutinas')
def lista_aulas_matutinas():
    aulas = Aula.select().where(Aula.periodo == 1).order_by(Aula.hora_inicio.asc())

    alterando_sessions_para_false()
    session['visualizando_aulas'] = True
    session['visualizando_aulas_matutinas'] = True
    
    return render_template("cadastro/aula_templates/lista_aulas_matutinas.html", aulas=aulas)

@aula_route.route('/lista_aulas_vespertinas')
def lista_aulas_vespertinas():
    aulas = Aula.select().where(Aula.periodo == 2).order_by(Aula.hora_inicio.asc())

    alterando_sessions_para_false()
    session['visualizando_aulas'] = True
    session['visualizando_aulas_vespertinas'] = True
    
    return render_template("cadastro/aula_templates/lista_aulas_vespertinas.html", aulas=aulas)

@aula_route.route('/lista_aulas_noturnas')
def lista_aulas_noturnas():
    aulas = Aula.select().where(Aula.periodo == 3).order_by(Aula.hora_inicio.asc())

    alterando_sessions_para_false()
    session['visualizando_aulas'] = True
    session['visualizando_aulas_noturnas'] = True
    
    return render_template("cadastro/aula_templates/lista_aulas_noturnas.html", aulas=aulas)

@aula_route.route('periodo-<int:periodo_id>/new')
def form_aula(periodo_id):

    periodos = Periodo.select()

    return render_template("cadastro/aula_templates/form_aula.html", periodo_id=periodo_id, periodos=periodos)

@aula_route.route('/', methods=["POST"])
def inserir_aula():
    data = request.form

    # Remove segundos da string de hora
    hora_inicio_str = data['hora_inicio'].split(':')[:2]  # Pega horas e minutos
    hora_termino_str = data['hora_termino'].split(':')[:2]
    hora_inicio = ':'.join(hora_inicio_str)
    hora_termino = ':'.join(hora_termino_str)

    # Converte para datetime.time
    hora_inicio = datetime.strptime(hora_inicio, "%H:%M").time()
    hora_termino = datetime.strptime(hora_termino, "%H:%M").time()

    # Valida se o horário de início é menor que o de término
    if hora_inicio >= hora_termino:
        flash("O horário de início deve ser menor que o horário de término!", "error")
        return redirect(url_for('cadastro.tela_cadastro'))

    # Definir limites de horário para cada período
    if data['periodo'] == "Matutino":
        periodo_id = 1
    elif data['periodo'] == "Vespertino":
        periodo_id = 2
    else:  # Noturno
        periodo_id = 3

    periodo = Periodo.get(Periodo.id == periodo_id)

    # Obtém os limites de hora do período
    inicio_periodo = periodo.hora_inicio
    fim_periodo = periodo.hora_termino

    # Verifica se o horário da aula está dentro dos limites do período
    if not (inicio_periodo <= hora_inicio < fim_periodo and inicio_periodo < hora_termino <= fim_periodo):
        flash(f"Os horários devem estar dentro do período {data['periodo']} ({inicio_periodo} ~ {fim_periodo})", "error")
        return redirect(url_for('cadastro.tela_cadastro'))

    # Verifica se já existe uma aula no mesmo período que sobrepõe os horários
    aulas_existentes = Aula.select().where(Aula.periodo == periodo_id)
    
    for aula in aulas_existentes:
        # Se o horário de início ou término da nova aula estiver dentro de uma aula existente, ou vice-versa
        if (aula.hora_inicio <= hora_inicio < aula.hora_termino) or (aula.hora_inicio < hora_termino <= aula.hora_termino) or (hora_inicio <= aula.hora_inicio < hora_termino):
            flash("O horário informado sobrepõe-se com outra aula já cadastrada!", "error")
            return redirect(url_for('cadastro.tela_cadastro'))

    # Cria a aula com os dados fornecidos
    Aula.create(
        periodo=periodo_id,
        hora_inicio=hora_inicio,
        hora_termino=hora_termino
    )

    # Incrementa a quantidade de aulas no período
    periodo.qtde_aulas += 1

    # Salva a instância do período
    periodo.save()

    # Armazena dados temporariamente na sessão
    session['visualizando_aulas'] = True

    return redirect(url_for('cadastro.tela_cadastro'))

@aula_route.route('periodo-<int:periodo_id>/<int:aula_id>/edit')
def form_edit_aula(aula_id, periodo_id):

    aula_selecionada = Aula.get_by_id(aula_id)

    periodos = Periodo.select()

    return render_template("cadastro/aula_templates/form_aula.html", aula=aula_selecionada, periodo_id=periodo_id, periodos=periodos)

@aula_route.route('/<int:aula_id>/update', methods=["POST"])
def atualizar_aula(aula_id):
    if request.form.get('_method') == "PUT":
        data = request.form

        # Remove segundos da string de hora
        hora_inicio_str = data['hora_inicio'].split(':')[:2]  # Pega horas e minutos
        hora_termino_str = data['hora_termino'].split(':')[:2]
        hora_inicio = ':'.join(hora_inicio_str)
        hora_termino = ':'.join(hora_termino_str)

        # Converte para datetime.time
        hora_inicio = datetime.strptime(hora_inicio, "%H:%M").time()
        hora_termino = datetime.strptime(hora_termino, "%H:%M").time()

        # Valida se o horário de início é menor que o de término
        if hora_inicio >= hora_termino:
            flash("O horário de início deve ser menor que o horário de término!", "error")
            return redirect(url_for('cadastro.tela_cadastro'))

        # Definir limites de horário para cada período
        if data['periodo'] == "Matutino":
            periodo_id = 1
        elif data['periodo'] == "Vespertino":
            periodo_id = 2
        else:  # Noturno
            periodo_id = 3

        periodo = Periodo.get(Periodo.id == periodo_id)

        # Obtém os limites de hora do período
        inicio_periodo = periodo.hora_inicio
        fim_periodo = periodo.hora_termino

        # Verifica se o horário da aula está dentro dos limites do período
        if not (inicio_periodo <= hora_inicio < fim_periodo and inicio_periodo < hora_termino <= fim_periodo):
            flash(f"Os horários devem estar dentro do período {data['periodo']} ({inicio_periodo} ~ {fim_periodo})", "error")
            return redirect(url_for('cadastro.tela_cadastro'))

        # Verifica se já existe uma aula no mesmo período que sobrepõe os horários
        aulas_existentes = Aula.select().where(Aula.periodo == periodo_id, Aula.id != aula_id)
        
        for aula in aulas_existentes:
            # Se o horário de início ou término da nova aula estiver dentro de uma aula existente, ou vice-versa
            if (aula.hora_inicio <= hora_inicio < aula.hora_termino) or (aula.hora_inicio < hora_termino <= aula.hora_termino) or (hora_inicio <= aula.hora_inicio < hora_termino):
                flash("O horário informado sobrepõe-se com outra aula já cadastrada!", "error")
                return redirect(url_for('cadastro.tela_cadastro'))

        # Atualiza a aula com os novos dados
        aula_atualizada = Aula.get_by_id(aula_id)
        aula_atualizada.periodo = periodo_id
        aula_atualizada.hora_inicio = hora_inicio
        aula_atualizada.hora_termino = hora_termino
        aula_atualizada.save()

    return redirect(url_for('cadastro.tela_cadastro'))

@aula_route.route('/<int:aula_id>/delete', methods=["DELETE"])
def deletar_aula(aula_id):

    aula = Aula.get_by_id(aula_id)
    periodo = Periodo.get_by_id(aula.periodo)

    aula.delete_instance()

    periodo.qtde_aulas -= 1
    periodo.save()

    return {"aula excluída": "ok"}