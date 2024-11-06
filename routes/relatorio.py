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
    
    return render_template("/relatorios/relatorio_templates/filtros/filtros_relatorio_geral.html")

@relatorio_route.route("/relatorio_geral", methods=["POST"])
def relatorio_geral():
    data = request.form

    periodo_inicial = data["periodo_inicial"]
    periodo_final = data["periodo_final"]

    # Converte as strings para objetos datetime
    periodo_inicial = datetime.strptime(periodo_inicial, "%Y-%m-%d")
    periodo_final = datetime.strptime(periodo_final, "%Y-%m-%d")

    # Verifica se o período final é maior que o período inicial
    if periodo_final < periodo_inicial:
        flash("O período final deve ser maior que o período inicial!", "error")
        return redirect(request.referrer)

    # Obtém uploads no período especificado que já foram analisados
    uploads = obter_uploads_no_periodo(periodo_inicial, periodo_final)

    # Obtém as análises relacionadas aos uploads
    analises = obter_analises_dos_uploads(uploads)

    # Calcula as contagens de cada classe para cada upload
    classes_por_upload = calcular_contagens_por_upload(uploads, analises)

    return render_template(
        "relatorios/relatorio_templates/paginas_relatorios/relatorio_geral.html", 
        uploads=uploads, 
        classes_por_upload=classes_por_upload
    )

@relatorio_route.route("/filtros_relatorio_agrupado")
def filtros_relatorio_agrupado():
    
    return render_template("/relatorios/relatorio_templates/filtros/filtros_relatorio_agrupado.html")

@relatorio_route.route("/relatorio_agrupado", methods=["POST"])
def relatorio_agrupado():
    dados = request.form

    periodo_inicial = dados["periodo_inicial"]
    periodo_final = dados["periodo_final"]
    agrupado_por = dados["agrupado_por"]

    # Converte as strings para objetos datetime
    periodo_inicial = datetime.strptime(periodo_inicial, "%Y-%m-%d")
    periodo_final = datetime.strptime(periodo_final, "%Y-%m-%d")

    # Verifica se o período final é maior que o período inicial
    if periodo_final < periodo_inicial:
        flash("O período final deve ser maior que o período inicial!", "error")
        return redirect(request.referrer)

    # Obtém uploads no período especificado que já foram analisados
    uploads = obter_uploads_no_periodo(periodo_inicial, periodo_final)

    # Obtém as análises relacionadas aos uploads
    analises = obter_analises_dos_uploads(uploads)

    # Calcula as contagens de cada classe para cada upload
    classes_por_upload = calcular_contagens_por_upload(uploads, analises)

    # Determina a classe mais comum por upload e calcula a soma da classe mais repetida
    classe_mais_comum, somas_por_upload = obter_classe_mais_comum_e_somas(classes_por_upload)

    # Agrupa os uploads com base no parâmetro 'agrupado_por'
    uploads_agrupados = agrupar_uploads(uploads, classe_mais_comum, agrupado_por)

    # Pré-processa os professores por upload para uso no template
    professores_por_upload = {upload.id: get_professores_for_upload(upload) for upload in uploads}

    return render_template(
        "relatorios/relatorio_templates/paginas_relatorios/relatorio_agrupado.html",
        grouped_uploads=uploads_agrupados,
        classe_mais_comum=classe_mais_comum,
        agrupado_por=agrupado_por,
        professores_por_upload=professores_por_upload,
        somas_por_upload=somas_por_upload
    )

def obter_uploads_no_periodo(periodo_inicial, periodo_final):
    """
    Obtém os uploads no período especificado que já foram analisados.
    """
    return Upload.select().where(
        (Upload.data_registro >= periodo_inicial) & 
        (Upload.data_registro <= periodo_final) & 
        (Upload.is_analisado == True)
    )

def obter_analises_dos_uploads(uploads):
    """
    Obtém as análises relacionadas aos uploads fornecidos.
    """
    upload_ids = [upload.id for upload in uploads]
    return Analise.select().where(Analise.upload_id.in_(upload_ids))

def calcular_contagens_por_upload(uploads, analises):
    """
    Calcula as contagens de cada classe para cada upload.
    """
    classes_por_upload = {upload.id: {
        'Dormindo': 0,
        'Prestando Atenção': 0,
        'Mexendo no Celular': 0,
        'Copiando': 0,
        'Disperso': 0,
        'Trabalho em Grupo': 0
    } for upload in uploads}

    for analise in analises:
        upload_id = analise.upload_id
        contagens = classes_por_upload[upload_id]
        contagens['Dormindo'] += analise.qtde_objeto_dormindo
        contagens['Prestando Atenção'] += analise.qtde_objeto_prestando_atencao
        contagens['Mexendo no Celular'] += analise.qtde_objeto_mexendo_celular
        contagens['Copiando'] += analise.qtde_objeto_copiando
        contagens['Disperso'] += analise.qtde_objeto_disperso
        contagens['Trabalho em Grupo'] += analise.qtde_objeto_trabalho_em_grupo

    return classes_por_upload

def obter_classe_mais_comum_e_somas(classes_por_upload):
    """
    Determina a classe mais comum por upload e calcula a soma da classe mais repetida.
    """
    classe_mais_comum = {}
    somas_por_upload = {}

    for upload_id, contagens in classes_por_upload.items():
        # Encontra a classe com a maior contagem
        max_classe = max(contagens, key=contagens.get)
        classe_mais_comum[upload_id] = max_classe
        soma_classe_mais_repetida = contagens[max_classe]
        somas_por_upload[upload_id] = soma_classe_mais_repetida

    return classe_mais_comum, somas_por_upload

def agrupar_uploads(uploads, classe_mais_comum, agrupado_por):
    """
    Agrupa os uploads com base no parâmetro 'agrupado_por'.
    """
    if agrupado_por == 'classificacoes':
        return agrupar_por_classificacao(uploads, classe_mais_comum)
    elif agrupado_por == 'aula':
        return agrupar_por_aula(uploads)
    else:
        return agrupar_por_outros(uploads, agrupado_por)

def agrupar_por_classificacao(uploads, classe_mais_comum):
    """
    Agrupa os uploads por classificações (Dormindo, Prestando Atenção, etc.).
    """
    classificacoes = ['Dormindo', 'Prestando Atenção', 'Mexendo no Celular',
                      'Copiando', 'Disperso', 'Trabalho em Grupo']
    uploads_agrupados = {classificacao: [] for classificacao in classificacoes}
    uploads_dict = {upload.id: upload for upload in uploads}

    for upload_id, max_classe in classe_mais_comum.items():
        uploads_agrupados[max_classe].append(uploads_dict[upload_id])

    return uploads_agrupados

def agrupar_por_aula(uploads):
    """
    Agrupa os uploads por período e por aula, garantindo a ordenação correta.
    """
    uploads_agrupados = {}
    periodos = set(upload.periodo for upload in uploads if upload.periodo is not None)
    periodo_aulas = {}  # {periodo_id: {aula_id: indice}}

    # Mapeia cada período para suas aulas ordenadas
    for periodo in periodos:
        aulas = Aula.select().where(Aula.periodo == periodo).order_by(Aula.hora_inicio)
        indice_aulas = {aula.id: indice for indice, aula in enumerate(aulas, start=1)}
        periodo_aulas[periodo.id] = indice_aulas

    for upload in uploads:
        periodo = upload.periodo
        nome_periodo = periodo.nome_periodo if periodo else 'Sem Período'

        # Obtém as aulas que correspondem ao upload
        aulas = get_aulas_for_upload(upload)  # Mantém a função existente
        if aulas:
            for aula in aulas:
                if periodo and periodo.id in periodo_aulas and aula.id in periodo_aulas[periodo.id]:
                    indice_aula = periodo_aulas[periodo.id][aula.id]
                    nome_aula = f"{indice_aula}ª Aula"

                    # Inicializa os dicionários aninhados se necessário
                    uploads_agrupados.setdefault(nome_periodo, {}).setdefault(nome_aula, []).append(upload)
        else:
            # Caso o upload não corresponda a nenhuma aula
            uploads_agrupados.setdefault(nome_periodo, {}).setdefault('Sem Aula', []).append(upload)

    # Ordena as aulas por seu índice (1ª, 2ª, etc.)
    for nome_periodo in uploads_agrupados:
        uploads_agrupados[nome_periodo] = dict(sorted(
            uploads_agrupados[nome_periodo].items(),
            key=lambda x: int(x[0].split('ª')[0]) if x[0].split('ª')[0].isdigit() else float('inf')
        ))

    return uploads_agrupados

def agrupar_por_outros(uploads, agrupado_por):
    """
    Agrupa os uploads por outras categorias (professor, disciplina, sala, etc.).
    """
    uploads_agrupados = {}
    for upload in uploads:
        chaves_agrupamento = []

        if agrupado_por == 'professor':
            professores = get_professores_for_upload(upload)  # Mantém a função existente
            chaves_agrupamento = professores if professores else ['Sem Professor']
        elif agrupado_por == 'disciplina':
            disciplinas = get_disciplinas_for_upload(upload)  # Mantém a função existente
            chaves_agrupamento = disciplinas if disciplinas else ['Sem Disciplina']
        elif agrupado_por == 'sala':
            chaves_agrupamento = [upload.sala.nome_sala] if upload.sala else ['Sem Sala']
        elif agrupado_por == 'turma':
            chaves_agrupamento = [upload.turma.nome_turma] if upload.turma else ['Sem Turma']
        elif agrupado_por == 'periodo':
            chaves_agrupamento = [upload.periodo.nome_periodo] if upload.periodo else ['Sem Período']
        else:
            chaves_agrupamento = ['Desconhecido']

        # Agrupa o upload em cada chave de agrupamento
        for chave in chaves_agrupamento:
            uploads_agrupados.setdefault(chave, []).append(upload)

    return uploads_agrupados

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