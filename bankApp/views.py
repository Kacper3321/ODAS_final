from flask import Blueprint, render_template, flash
from flask_login import login_required, current_user
from . import db
from .models import UserSensitiveData
from .encryptSensData import decrypt_aes
from dotenv import load_dotenv
from os import environ

views = Blueprint("views", __name__)


@views.route("/")
@views.route("/home")
@login_required
def home():
    sekret = ""
    if current_user.login_count == 1:
        #pobranie klucza ze zmiennej srodowiskowej w moim przypadku nie udostepniony plik .env przechowywany lokalnie 
        aes_key = environ.get('aes_key')
        auth_code = UserSensitiveData.query.filter_by(user_id=current_user.id).first()
        sekret = decrypt_aes(auth_code.auth_code, aes_key)  #pobranie sekretu i odszyfrowanie go zeby uzytkownik mogl odczytac swoj sekret i zapisac w bezpiecznym miejscu lub zapamietac
        db.session.commit()

    return render_template("home.html", user=current_user, count=current_user.login_count, sekret=sekret)