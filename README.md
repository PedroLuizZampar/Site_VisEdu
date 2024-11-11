# VisEdu

#### Projeto de Visão Computacional Direcionado à Educação

## 🚀 Começando

Essas instruções permitirão que você obtenha uma cópia do projeto em operação na sua máquina local para fins de desenvolvimento e teste.

### 📋 Pré-requisitos

- [Python3](https://www.python.org/downloads/release/python-3130/)
- [Visual Studio Code](https://code.visualstudio.com/)
- [MySQL Workbench](https://www.mysql.com/products/workbench/)

### 💡 Recomendáveis
- [Git](https://git-scm.com/downloads)

### 🔧 Preparando o ambiente

Para executar o projeto, precisamos clonar este repositório em nossa máquina local. Em seguida, devemos instalar algumas dependências mas antes é preciso criar um ambiente virtual para maior organização e controle sobre as bibliotecas usadas no projeto.

#### Criando clone do projeto
``` bash
git clone https://github.com/PedroLuizZampar/Site_VisEdu.git
```
#### ou faça o [download do arquivo ZIP](https://github.com/PedroLuizZampar/Site_VisEdu/archive/refs/heads/main.zip)
<hr>

#### Acessando a pasta do projeto
``` bash
cd Site_VisEdu
```
<hr>

#### Criação do ambiente virtual
``` bash
python3 -m venv venv
```
<hr>

#### Ativando o ambiente - (Linux)
``` bash
source venv/bin/activate
```

#### Ativando o ambiente - (Windows)
``` bash
venv\Scripts\Activate
```
<hr>

#### Instalando todas as dependências
``` bash
pip install -r requirements.txt  
```

#### Criando arquivo de ambiente (.env)
``` bash
touch .env
```
<hr>

#### Adicione as informações necessárias para a conexão com o banco de dados
``` bash
NOME_BANCO=nome_aqui
USUARIO=usuario_aqui
SENHA=senha_aqui
HOST=host_aqui
PORTA=porta_aqui
```

## ⚙️ Executando o projeto

Para executar o projeto, verifique se o ambiente virtual está ativo.

#### Ativando o ambiente - (Linux)
``` bash
source venv/bin/activate
```

#### Ativando o ambiente - (Windows)
``` bash
venv\Scripts\Activate
```
<hr>

#### Iniciando a aplicação
``` bash
python main.py
```
<hr>

#### Acessando a aplicação
Após iniciada, a aplicação estareá rodando em ambiente local na porta 5000. Para acessar, basta acessar o link: [localhost:5000](http://localhost:5000)

## 🛠️ Construído com

* [Flask](https://flask.palletsprojects.com/en/stable/) - O framework web usado
* [PeeWee](https://docs.peewee-orm.com/en/latest/) - ORM utilizado para integração com o banco de dados
* [Cru.js](https://github.com/Iazzetta/cru.js) - Biblioteca utilizada para facilitar a utilização de requisições CRUD. Créditos pela criação da biblioteca:
    - GitHub: [lazzeta](https://github.com/Iazzetta/)
    - YouTube: [Programador Python](https://www.youtube.com/@programadorpython)

## ✒️ Autores

* **Idealizador do Projeto e Programador FullStack**
    - GitHub: [PedroLuizZampar](https://github.com/PedroLuizZampar)
    - LinkedIn: [Pedro Luiz Pereira Zampar](https://www.linkedin.com/in/pedro-luiz-pereira-zampar-533724269/)
* **Redator e Facilitador**
    - GitHub: [leonardobarbonabreu](https://github.com/leonardobarbonabreu)
    - LinkedIn: [Leonardo José Barbon de Abreu](https://www.linkedin.com/in/leonardo-jos%C3%A9-barbon-de-abreu-4b2723269/)
* **Criador da Identidade Visual e Designer**
    - GitHub: [andreluissantosdecamargo](https://github.com/andreluissantosdecamargo)
    - LinkedIn: [André Luís Santos de Camargo](https://www.linkedin.com/in/andreezxs/)