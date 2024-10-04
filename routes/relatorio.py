from flask import Blueprint, url_for, render_template, redirect, flash, session, request
from datetime import datetime
from funcoes_extras import alterando_sessions_para_false
from database.models.analise import Analise
from database.models.upload import Upload
from database.models.aula import Aula
from database.models.aula_professor import Aula_Professor
from database.models.professor import Professor

relatorio_route = Blueprint("relatorio", __name__)

@relatorio_route.route('/')
def tela_relatorio():
    # Busca as sessões e atribui um valor padrão de None caso ainda não estejam ativas
    visualizando_relatorios = session.pop('visualizando_relatorios', None)

    session['visualizando_relatorios'] = True
    
    return render_template('relatorios/index.html', visualizando_relatorios=visualizando_relatorios) # Se não ouver um session ativa, retorna a página sem parâmetros

@relatorio_route.route("/opcoes_relatorio")
def lista_opcoes_relatorios():
    alterando_sessions_para_false()
    session['visualizando_relatorios'] = True

    return render_template("relatorios/relatorio_templates/lista_opcoes_relatorios.html")

@relatorio_route.route("/filtros_relatorio")
def filtros_relatorio():

    return render_template("/relatorios/relatorio_templates/filtros_relatorio.html")

@relatorio_route.route("/relatorio_geral", methods=["POST"])
def relatorio_geral():
    data = request.form

    periodo_inicial = data["periodo_inicial"]
    periodo_final = data["periodo_final"]

    uploads = Upload.select().where(
        (Upload.data_registro >= periodo_inicial) & 
        (Upload.data_registro <= periodo_final) & 
        (Upload.is_analisado == True)
    )

    analises = Analise.select().where(Analise.upload_id.in_([upload.id for upload in uploads]))

    professores_por_upload = {}
    soma_qtde_objetos = {upload.id: 0 for upload in uploads}  # Inicializa o dicionário para somar qtde_objetos
    
    # Iterar sobre os uploads e encontrar os professores correspondentes
    for upload in uploads:
        # Buscar aulas que coincidem com o período e horário do upload
        aulas = Aula.select().where(
            (Aula.periodo == upload.periodo) &
            (Aula.hora_inicio < upload.hora_termino) &  # A aula deve começar antes do upload terminar
            (Aula.hora_termino > upload.hora_registro)  # A aula deve terminar depois do upload começar
        )

        # Determinar o dia da semana do upload
        dia_semana_upload = upload.data_registro.strftime("%A")
        
        match dia_semana_upload.lower():
            case "monday":
                dia_semana_upload = "segunda-feira"
            case "tuesday":
                dia_semana_upload = "terça-feira"
            case "wednesday":
                dia_semana_upload = "quarta-feira"
            case "thursday":
                dia_semana_upload = "quinta-feira"
            case "friday":
                dia_semana_upload = "sexta-feira"
            case "saturday":
                dia_semana_upload = "sabado"
            case "sunday":
                dia_semana_upload = "domingo"

        # Buscar professores para cada aula correspondente ao dia da semana
        professores = (
            Professor
            .select(Professor.nome_professor)
            .join(Aula_Professor)
            .where(
                (Aula_Professor.aula.in_(aulas)) & 
                (Aula_Professor.dia_semana == dia_semana_upload)  # Filtra pelo dia da semana
            )
        )
        
        professores_por_upload[upload.id] = [professor.nome_professor for professor in professores]

    # Acumula a soma de qtde_objetos por upload
    for analise in analises:
        soma_qtde_objetos[analise.upload_id] += analise.qtde_objetos

    return render_template(
        "relatorios/relatorio_templates/relatorio_geral.html", 
        uploads=uploads, 
        analises=analises, 
        professores_por_upload=professores_por_upload,
        soma_qtde_objetos=soma_qtde_objetos  # Passa a soma para o template
    )
