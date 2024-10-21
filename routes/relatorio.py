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

@relatorio_route.route("/filtros_relatorio_geral")
def filtros_relatorio_geral():
    
    return render_template("/relatorios/relatorio_templates/filtros_relatorio_geral.html")

@relatorio_route.route("/relatorio_geral", methods=["POST"])
def relatorio_geral():
    data = request.form

    periodo_inicial = data["periodo_inicial"]
    periodo_final = data["periodo_final"]

    # Obtém os uploads no período especificado que já foram analisados
    uploads = Upload.select().where(
        (Upload.data_registro >= periodo_inicial) & 
        (Upload.data_registro <= periodo_final) & 
        (Upload.is_analisado == True)
    )

    # Obtém os uploads no período especificado que já foram analisados
    analises = Analise.select().where(Analise.upload_id.in_([upload.id for upload in uploads]))

    # Dicionário para armazenar as contagens de cada classe por upload
    classes_por_upload = {upload.id: {
        'Dormindo': 0,
        'Prestando Atenção': 0,
        'Mexendo no Celular': 0,
        'Copiando': 0,
        'Disperso': 0,
        'Trabalho em Grupo': 0
    } for upload in uploads}

    # Calcula as contagens de cada classe para cada upload
    for analise in analises:
        upload_id = analise.upload_id
        counts = classes_por_upload[upload_id]
        counts['Dormindo'] += analise.qtde_objeto_dormindo
        counts['Prestando Atenção'] += analise.qtde_objeto_prestando_atencao
        counts['Mexendo no Celular'] += analise.qtde_objeto_mexendo_celular
        counts['Copiando'] += analise.qtde_objeto_copiando
        counts['Disperso'] += analise.qtde_objeto_disperso
        counts['Trabalho em Grupo'] += analise.qtde_objeto_trabalho_em_grupo

    # Dicionário para armazenar a classe que mais se repete por upload
    classe_mais_comum = {}

    for upload_id, counts in classes_por_upload.items():
        # Encontra a classe com a maior contagem
        max_class = max(counts, key=counts.get)
        classe_mais_comum[upload_id] = max_class

    # Obtém os professores associados a cada upload usando a função auxiliar
    professores_por_upload = {}
    for upload in uploads:
        professores_por_upload[upload.id] = get_professores_for_upload(upload)

    return render_template(
        "relatorios/relatorio_templates/relatorio_geral.html", 
        uploads=uploads, 
        analises=analises, 
        professores_por_upload=professores_por_upload,
        classe_mais_comum=classe_mais_comum
    )

@relatorio_route.route("/filtros_relatorio_agrupado")
def filtros_relatorio_agrupado():
    
    return render_template("/relatorios/relatorio_templates/filtros_relatorio_agrupado.html")

@relatorio_route.route("/relatorio_agrupado", methods=["POST"])
def relatorio_agrupado():
    data = request.form

    periodo_inicial = data["periodo_inicial"]
    periodo_final = data["periodo_final"]
    agrupado_por = data["agrupado_por"]

    # Obtém uploads no período especificado que já foram analisados
    uploads = Upload.select().where(
        (Upload.data_registro >= periodo_inicial) &
        (Upload.data_registro <= periodo_final) &
        (Upload.is_analisado == True)
    )

    # Obtém os uploads no período especificado que já foram analisados
    analises = Analise.select().where(Analise.upload_id.in_([upload.id for upload in uploads]))

    # Dicionário para armazenar as contagens de cada classe por upload
    classes_por_upload = {upload.id: {
        'Dormindo': 0,
        'Prestando Atenção': 0,
        'Mexendo no Celular': 0,
        'Copiando': 0,
        'Disperso': 0,
        'Trabalho em Grupo': 0
    } for upload in uploads}

    # Calcula as contagens de cada classe para cada upload
    for analise in analises:
        upload_id = analise.upload_id
        counts = classes_por_upload[upload_id]
        counts['Dormindo'] += analise.qtde_objeto_dormindo
        counts['Prestando Atenção'] += analise.qtde_objeto_prestando_atencao
        counts['Mexendo no Celular'] += analise.qtde_objeto_mexendo_celular
        counts['Copiando'] += analise.qtde_objeto_copiando
        counts['Disperso'] += analise.qtde_objeto_disperso
        counts['Trabalho em Grupo'] += analise.qtde_objeto_trabalho_em_grupo

    # Dicionário para armazenar a classe que mais se repete por upload
    classe_mais_comum = {}

    for upload_id, counts in classes_por_upload.items():
        # Encontra a classe com a maior contagem
        max_class = max(counts, key=counts.get)
        classe_mais_comum[upload_id] = max_class

    # Dicionário para agrupar os uploads
    grouped_uploads = {}

    if agrupado_por == 'aula':
        # Agrupamento duplo: por período e por aula ordenada

        # Obtém todos os períodos presentes nos uploads
        periodos = set(upload.periodo for upload in uploads if upload.periodo is not None)

        # Dicionário que mapeia cada período para suas aulas ordenadas
        periodo_aulas = {}  # {periodo_id: {aula_id: index}}

        for periodo in periodos:
            # Obtém todas as aulas do período atual, ordenadas por hora de início
            aulas = Aula.select().where(Aula.periodo == periodo).order_by(Aula.hora_inicio)
            aula_indices = {}
            # Enumera as aulas para atribuir índices (1ª Aula, 2ª Aula, etc.)
            for index, aula in enumerate(aulas, start=1):
                aula_indices[aula.id] = index
            periodo_aulas[periodo.id] = aula_indices

        # Agrupa uploads por período e por aula
        for upload in uploads:
            periodo = upload.periodo
            periodo_nome = periodo.nome_periodo if periodo else 'Sem Período'

            # Obtém as aulas que correspondem ao upload
            aulas = get_aulas_for_upload(upload)
            if aulas:
                for aula in aulas:
                    if periodo and periodo.id in periodo_aulas and aula.id in periodo_aulas[periodo.id]:
                        # Obtém o índice da aula (1ª Aula, 2ª Aula, etc.)
                        aula_index = periodo_aulas[periodo.id][aula.id]
                        aula_nome = f"{aula_index}ª Aula"
                    else:
                        aula_nome = 'Sem Aula'

                    # Inicializa os dicionários aninhados se necessário
                    if periodo_nome not in grouped_uploads:
                        grouped_uploads[periodo_nome] = {}
                    if aula_nome not in grouped_uploads[periodo_nome]:
                        grouped_uploads[periodo_nome][aula_nome] = []
                    # Adiciona o upload ao grupo correspondente
                    grouped_uploads[periodo_nome][aula_nome].append(upload)
            else:
                # Caso o upload não corresponda a nenhuma aula
                if periodo_nome not in grouped_uploads:
                    grouped_uploads[periodo_nome] = {}
                if 'Sem Aula' not in grouped_uploads[periodo_nome]:
                    grouped_uploads[periodo_nome]['Sem Aula'] = []
                grouped_uploads[periodo_nome]['Sem Aula'].append(upload)
    else:
        # Agrupamentos simples por outras categorias
        for upload in uploads:
            grouping_keys = []

            if agrupado_por == 'professor':
                professores = get_professores_for_upload(upload)
                grouping_keys = professores if professores else ['Sem Professor']

            elif agrupado_por == 'disciplina':
                disciplinas = get_disciplinas_for_upload(upload)
                grouping_keys = disciplinas if disciplinas else ['Sem Disciplina']

            elif agrupado_por == 'sala':
                grouping_keys = [upload.sala.nome_sala] if upload.sala else ['Sem Sala']

            elif agrupado_por == 'turma':
                grouping_keys = [upload.turma.nome_turma] if upload.turma else ['Sem Turma']

            elif agrupado_por == 'periodo':
                grouping_keys = [upload.periodo.nome_periodo] if upload.periodo else ['Sem Período']

            else:
                grouping_keys = ['Desconhecido']

            # Agrupa o upload em cada chave de agrupamento
            for key in grouping_keys:
                if key not in grouped_uploads:
                    grouped_uploads[key] = []
                grouped_uploads[key].append(upload)

    # Pré-processa os professores por upload para uso no template
    professores_por_upload = {}
    for upload in uploads:
        professores_por_upload[upload.id] = get_professores_for_upload(upload)

    return render_template(
        "relatorios/relatorio_templates/relatorio_agrupado.html",
        grouped_uploads=grouped_uploads,
        classe_mais_comum=classe_mais_comum,
        agrupado_por=agrupado_por,
        professores_por_upload=professores_por_upload
    )

def get_professores_for_upload(upload):
    professores_set = set()

    # Busca aulas que coincidem com o período e horário do upload
    aulas = Aula.select().where(
        (Aula.periodo == upload.periodo) &
        (Aula.hora_inicio < upload.hora_termino) &  # A aula deve começar antes do upload terminar
        (Aula.hora_termino > upload.hora_registro)  # A aula deve terminar depois do upload começar
    )

    # Determina o dia da semana do upload em inglês
    dia_semana_upload = upload.data_registro.strftime("%A")

    # Mapear o dia da semana para português
    dias_semana = {
        "Monday": "segunda-feira",
        "Tuesday": "terça-feira",
        "Wednesday": "quarta-feira",
        "Thursday": "quinta-feira",
        "Friday": "sexta-feira",
        "Saturday": "sabado",
        "Sunday": "domingo"
    }
    dia_semana_upload = dias_semana.get(dia_semana_upload, dia_semana_upload)

    # Busca professores associados às aulas naquele dia da semana
    professores = (
        Professor
        .select(Professor.nome_professor, Aula, Aula_Professor)
        .join(Aula_Professor, on=(Professor.id == Aula_Professor.professor_id))
        .join(Aula, on=(Aula_Professor.aula_id == Aula.id))
        .where(
            (Aula.id.in_([aula.id for aula in aulas])) &  # Aulas correspondentes
            (Aula_Professor.dia_semana == dia_semana_upload)  # Mesmo dia da semana
        )
    )

    # Filtra professores cujas aulas coincidem com o horário e turma do upload
    for professor in professores:
        if (
            professor.aula_professor.aula.hora_inicio < upload.hora_termino and
            professor.aula_professor.aula.hora_termino > upload.hora_registro and
            professor.aula_professor.turma == upload.turma
        ):
            professores_set.add(professor.nome_professor)

    # Retorna uma lista de nomes de professores associados ao upload
    return list(professores_set)

def get_disciplinas_for_upload(upload):
    disciplinas_set = set()
    # Obtém os professores associados ao upload
    professores = get_professores_for_upload(upload)
    for professor_nome in professores:
        try:
            # Busca o professor pelo nome
            professor = Professor.get(Professor.nome_professor == professor_nome)
            if professor.disciplina:
                # Adiciona o nome da disciplina ao conjunto
                disciplinas_set.add(professor.disciplina.nome_disciplina)
        except Professor.DoesNotExist:
            continue  # Ignora se o professor não for encontrado
    # Retorna uma lista de disciplinas associadas ao upload
    return list(disciplinas_set)

def get_aulas_for_upload(upload):
    # Busca aulas que coincidem com o período e horário do upload
    aulas = Aula.select().where(
        (Aula.periodo == upload.periodo) &  # Mesmo período
        (Aula.hora_inicio < upload.hora_termino) &  # A aula começa antes do upload terminar
        (Aula.hora_termino > upload.hora_registro)  # A aula termina depois do upload começar
    )
    # Retorna uma lista de aulas correspondentes
    return aulas
