from datetime import datetime, time, timedelta
from flask import Blueprint, url_for, render_template, redirect, flash, session, request
from database.models.periodo import Periodo
from database.models.aula import Aula
from funcoes_extras import alterando_sessions_para_false

periodo_route = Blueprint("periodo", __name__)


@periodo_route.route('/')
def lista_periodos():

    periodos = Periodo.select()

    alterando_sessions_para_false()
    session['visualizando_periodos'] = True

    return render_template("cadastro/periodo_templates/lista_periodos.html", periodos=periodos)

@periodo_route.route('<int:periodo_id>/edit')
def form_periodo(periodo_id):

    periodo_selecionado = Periodo.get_by_id(periodo_id)

    return render_template("cadastro/periodo_templates/form_periodo.html", periodo=periodo_selecionado)

from datetime import datetime

@periodo_route.route('/<int:periodo_id>/update', methods=["POST"])
def atualizar_periodo(periodo_id):
    if request.form.get('_method') == "PUT":
        data = request.form

        # Carrega o período e as aulas atuais
        periodo_editado = Periodo.get_by_id(periodo_id)
        aulas_periodo = Aula.select().where(Aula.periodo == periodo_editado)
        quantidade_atual_aulas = aulas_periodo.count()

        # Remove os segundos da string (se presentes)
        hora_inicio_str = data['hora_inicio'].split(':')[:2]  # Pega apenas horas e minutos
        hora_inicio = ':'.join(hora_inicio_str)  # Reconstrói a string no formato HH:MM
        hora_termino_str = data['hora_termino'].split(':')[:2]
        hora_termino = ':'.join(hora_termino_str)

        # Converte para datetime.time
        hora_inicio = datetime.strptime(hora_inicio, "%H:%M").time()
        hora_termino = datetime.strptime(hora_termino, "%H:%M").time()

        # Validação 1: Verifica se o horário de início é menor que o de término no próprio formulário
        if hora_inicio >= hora_termino:
            flash("O horário de início deve ser menor que o horário de término!", "error")
            return redirect(url_for('cadastro.tela_cadastro'))

        # Atualiza os horários no período
        periodo_editado.hora_inicio = hora_inicio
        periodo_editado.hora_termino = hora_termino

        # Validação 2: Verifica se o novo período se sobrepõe a outros períodos

        # Seleciona outros períodos da mesma turma (ou outra entidade) que não sejam o período editado
        periodos_existentes = Periodo.select().where(
            (Periodo.id != periodo_editado.id)
        )

        # Verifica se as horas se sobrepõem
        for periodo in periodos_existentes:
            if (hora_inicio < periodo.hora_termino and hora_termino > periodo.hora_inicio):
                flash("O período informado se sobrepõe a outro período existente!", "error")
                return redirect(url_for('cadastro.tela_cadastro'))

        # Atualiza a quantidade de aulas do período
        nova_qtde_aulas = int(data['qtde_aulas'])
        periodo_editado.qtde_aulas = nova_qtde_aulas

        # Se a nova quantidade for maior, adiciona aulas
        if nova_qtde_aulas > quantidade_atual_aulas:
            diferenca = nova_qtde_aulas - quantidade_atual_aulas

            # Obtém a última aula como referência (se existir)
            ultima_aula = aulas_periodo.order_by(Aula.id.desc()).first()

            for i in range(diferenca):
                if ultima_aula:
                    # Converte a hora_inicio e hora_termino da última aula para datetime
                    ultima_hora_inicio = datetime.combine(datetime.today(), ultima_aula.hora_inicio)
                    ultima_hora_termino = datetime.combine(datetime.today(), ultima_aula.hora_termino)

                    # Adiciona o timedelta de 50 minutos
                    nova_hora_inicio = (ultima_hora_termino + timedelta(minutes=1)).time()
                    nova_hora_termino = (ultima_hora_termino + timedelta(minutes=2)).time()

                    # Cria nova aula com base na última aula
                    nova_aula = Aula.create(
                        periodo=periodo_editado,
                        hora_inicio=nova_hora_inicio,
                        hora_termino=nova_hora_termino
                    )
                    ultima_aula = nova_aula  # Atualiza a referência para a próxima aula
                else:
                    horario_incio_aula_formatado = datetime.combine(datetime.today(), periodo_editado.hora_inicio) + timedelta(minutes=i)
                    horario_termino_aula_formatado = datetime.combine(datetime.today(), periodo_editado.hora_inicio) + timedelta(minutes=i+1)
                    # Se não houver aula anterior, usa o horário do período
                    Aula.create(
                        periodo=periodo_editado,
                        hora_inicio=horario_incio_aula_formatado,
                        hora_termino=horario_termino_aula_formatado
                    )

        # Se a nova quantidade for menor, remove aulas do final para o início
        elif nova_qtde_aulas < quantidade_atual_aulas:
            diferenca = quantidade_atual_aulas - nova_qtde_aulas

            # Remove aulas excedentes de baixo para cima
            aulas_remover = aulas_periodo.order_by(Aula.id.desc()).limit(diferenca)
            for aula in aulas_remover:
                aula.delete_instance()

        # Salva as alterações no período
        periodo_editado.save()

        return redirect(url_for('cadastro.tela_cadastro'))
