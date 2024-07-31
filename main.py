from flask import Flask
from configuration import configure_all

# Inicialização
app = Flask(__name__)

# Configuração das rotas e do banco de dados
configure_all(app)

# Execução
if __name__ == "__main__":
    app.run(debug=True) # Quando um arquivo for salvop após uma modificação, o servidor é instantaneamente reiniciado
