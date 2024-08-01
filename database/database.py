import os
from peewee import MySQLDatabase
from dotenv import load_dotenv

# Carrega as variáveis de ambiente no arquivo .env
load_dotenv()

# Conexão com o banco de dados
db = MySQLDatabase(
    os.getenv('NOME_BANCO', ''),
    user=os.getenv('USUARIO', ''),
    password=os.getenv('SENHA', ),
    host=os.getenv('HOST', ''),
    port=int(os.getenv('PORTA', ''))
)