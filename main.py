import os
from flask import Flask
from configuration import configure_all

# Inicialização
app = Flask(__name__)

# Obtém a chave secreta de uma variável de ambiente
app.secret_key = os.environ.get('SECRET_KEY', 'default_secret_key')

# Configuração das rotas e do banco de dados
configure_all(app)

# Execução
if __name__ == "__main__":
    app.run(debug=True) # Quando um arquivo for salvo após uma modificação, o servidor é instantaneamente reiniciado
