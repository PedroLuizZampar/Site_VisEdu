from flask import Flask
from routes.home import home_route
from routes.upload import upload_route

app = Flask(__name__)

app.register_blueprint(home_route) # prefix = "/"
app.register_blueprint(upload_route, url_prefix = "/uploads")

# execução
if __name__ == "__main__":
    app.run(debug=True) # Quando um arquivo for salvop após uma modificação, o servidor é instantaneamente reiniciado
