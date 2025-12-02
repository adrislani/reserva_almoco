from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    # Configuração do banco de dados
    app.secret_key = "adriswyll" 
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://user08:user08@ricardosekeff.digital:3306/db_equipe08'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    migrate.init_app(app, db)
    from . import models

    from .routes import main
    app.register_blueprint(main)

    return app