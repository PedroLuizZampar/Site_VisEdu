from flask import Blueprint, url_for, render_template, redirect, flash, session, request
from database.models.disciplina import Disciplina
from funcoes_extras import alterando_sessions_para_false

disciplina_route = Blueprint("disciplina", __name__)


@disciplina_route.route('/')
def lista_disciplinas():

    disciplinas = Disciplina.select()

    alterando_sessions_para_false()
    session['visualizando_disciplinas'] = True

    return render_template("cadastro/disciplina_templates/lista_disciplinas.html", disciplinas=disciplinas)

@disciplina_route.route('/new')
def form_disciplina():

    return render_template("cadastro/disciplina_templates/form_disciplina.html")

@disciplina_route.route('/', methods=["POST"])
def inserir_disciplina():
    data = request.form

    disciplina_existente_nome = Disciplina.select().where(Disciplina.nome_disciplina == data['nome_disciplina']).first()

    if disciplina_existente_nome:
        flash("Já existe uma disciplina cadastrada com esse nome!", "error")
        return redirect(url_for('cadastro.tela_cadastro'))

    Disciplina.create(
        nome_disciplina=data['nome_disciplina']
    )

    # Armazena dados temporariamente na sessão
    session['visualizando_disciplinas'] = True

    return redirect(url_for('cadastro.tela_cadastro'))

@disciplina_route.route('<int:disciplina_id>/edit')
def form_edit_disciplina(disciplina_id):

    disciplina_selecionada = Disciplina.get_by_id(disciplina_id)

    return render_template("cadastro/disciplina_templates/form_disciplina.html", disciplina=disciplina_selecionada)

@disciplina_route.route('/<int:disciplina_id>/update', methods=["POST"])
def atualizar_disciplina(disciplina_id):
    if request.form.get('_method') == "PUT":
        data = request.form

        disciplina_existente_nome = Disciplina.select().where(
            (Disciplina.nome_disciplina == data['nome_disciplina']) & (Disciplina.id != disciplina_id)
            ).first()
        
        if disciplina_existente_nome:
            flash("Já existe uma disciplina cadastrada com esse nome!", "error")
            return redirect(url_for('cadastro.tela_cadastro'))

        disciplina_editada = Disciplina.get_by_id(disciplina_id)

        disciplina_editada.nome_disciplina = data['nome_disciplina']

        disciplina_editada.save()

    return redirect(url_for('cadastro.tela_cadastro'))

@disciplina_route.route('/<int:disciplina_id>/delete', methods=["DELETE"])
def deletar_disciplina(disciplina_id):

    disciplina = Disciplina.get_by_id(disciplina_id)

    disciplina.delete_instance()

    return {"disciplina excluída": "ok"}