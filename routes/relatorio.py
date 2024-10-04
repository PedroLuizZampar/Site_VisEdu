from flask import Blueprint, url_for, render_template, redirect, flash, session, request
from funcoes_extras import alterando_sessions_para_false
from database.models.analise import Analise
from database.models.upload import Upload
from database.models.upload import Periodo
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

    uploads = Upload.select().where(Upload.data_registro >= periodo_inicial and Upload.data_registro <= periodo_final and Upload.is_analisado == 1)
    analises = Analise.select().where(Analise.upload_id == next(iter(uploads), None))

    return render_template("relatorios/relatorio_templates/relatorio_geral.html", uploads=uploads, analises=analises)