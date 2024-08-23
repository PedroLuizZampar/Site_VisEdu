from flask import session

# Altera todas as sessions para false
def alterando_sessions_para_false():
    session['visualizando_salas'] = False
    session['visualizando_uploads_nao_analisados'] = False
    session['visualizando_uploads_analisados'] = False