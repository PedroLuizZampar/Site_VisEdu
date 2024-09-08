from flask import session
from database.models.turma import Turma
from database.models.upload import Upload

# Altera todas as sessions para false
def alterando_sessions_para_false():
    session['visualizando_salas'] = False
    session['visualizando_uploads_nao_analisados'] = False
    session['visualizando_uploads_analisados'] = False
    session['visualizando_turmas'] = False

def atualizando_turma_upload():
    turmas = Turma.select()
    uploads = Upload.select()

    for upload in uploads:
        for turma in turmas:
            if upload.turma == None and turma.sala == upload.sala and turma.periodo == upload.periodo:
                upload.turma = turma
                upload.save()
                break
            elif turma.sala != upload or turma.periodo != upload.periodo:
                verificar_turmas(upload)

def verificar_turmas(upload):
    turmas = Turma.select()

    for turma in turmas:
        if upload.turma == None and turma.sala == upload.sala and turma.periodo == upload.periodo:
            upload.turma = turma
            break
        else:
            upload.turma = None

    
    upload.save()