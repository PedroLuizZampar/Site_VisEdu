from flask import Blueprint, url_for, render_template, redirect, flash, request
from database.models.turma import Turma

turma_route = Blueprint("turma", __name__)

@turma_route.route('/')
def lista_turmas():

    turmas = Turma.select()

    return render_template("lista_turmas.html", turmas=turmas)

@turma_route.route('/actions_lista')
def actions_lista():

    return render_template("actions_lista_turma.html")