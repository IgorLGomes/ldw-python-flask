from flask import Flask, render_template
import pymysql
from controllers import routes
from models.database import db
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, template_folder='views')
routes.init_app(app)

# Prefer the secret key from .env for stable sessions across restarts
app.secret_key = os.getenv("FLASK_SECRET_KEY")

DB_NAME = "albums"
app.config['DATABASE_NAME'] = DB_NAME
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/albums'
app.config['SECRET_KEY'] = 'albumssecret'
app.config['PERMANENT_SESSION_LIFETIME'] = 1800
if __name__ == '__main__':
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password='',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    # Tentando criar o banco
    # Try, trata o sucesso
    try:
        # with cria um recurso temporariamente
        with connection.cursor() as cursor:  # alias
            # Cria o banco de dados (se ele não existir)
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
            print(f"O banco de dados {DB_NAME} está criado!")
    # Except, trata a falha
    except Exception as e:
        print(f"Erro ao criar o banco de dados: {e}")
    finally:
        connection.close()

    # Passando o flask para SQLAlchemy
    db.init_app(app=app)

    # Criando as tabelas a partir do model
    with app.test_request_context():
        db.create_all()

    app.run(host='0.0.0.0', port=4000, debug=True)
