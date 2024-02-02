from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path, environ
from flask_login import LoginManager
from dotenv import load_dotenv

load_dotenv()
db = SQLAlchemy()
DB_NAME = "banking.db"

def create_app():
    app = Flask(__name__)
    app.secret_key = environ.get('SECRET_KEY')  #sekretny klucz do podpisywania danych w sesji
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'  #okreslenie bazy danych dla projektu
    db.init_app(app)

    from .views import views
    from .auth import auth
    from .changePass import change_pass
    from .transaction import transaction
    from .makeTransaction import makeTransaction
    from .showSensData import show_sens_data

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")
    app.register_blueprint(change_pass, url_prefix='/auth')
    app.register_blueprint(transaction, url_prefix='/')
    app.register_blueprint(makeTransaction, url_prefix='/')
    app.register_blueprint(show_sens_data, url_prefix='/')

    from .models import User

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app

#tworze baze danych jesli jeszce jej nie ma w projekcie
def create_database(app):
    with app.app_context():
        if not path.exists("bankApp/" + DB_NAME):
            db.create_all()
            print("Created database!")