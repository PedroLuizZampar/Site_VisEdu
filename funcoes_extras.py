from flask import session
from database.models.turma import Turma
from database.models.upload import Upload

# Altera todas as sessions para false
def alterando_sessions_para_false():
    session['visualizando_salas'] = False
    session['visualizando_uploads_nao_analisados'] = False
    session['visualizando_uploads_analisados'] = False
    session['visualizando_turmas'] = False
    session['visualizando_disciplinas'] = False
    session['visualizando_cadastros'] = False
    session['visualizando_uploads'] = False
    session['visalizando_index'] = False

def atualizando_turma_upload():
    # Cria um dicionário onde a chave é uma tupla (sala, período) e o valor é o objeto turma correspondente
    # Isso facilita a busca de uma turma pelo par sala e período, tornando a verificação mais eficiente
    turmas = { (turma.sala, turma.periodo): turma for turma in Turma.select() }
    
    uploads = Upload.select()

    for upload in uploads:
        # Verifica se o upload ainda não tem turma
        if upload.turma is None:
            # Busca no dicionário a turma correspondente à sala e período do upload
            turma = turmas.get((upload.sala, upload.periodo))
            
            if turma:
                upload.turma = turma  # Se encontrou a turma, associa ao upload
            else:
                upload.turma = None  # Caso contrário, deixa como None

            upload.save()
