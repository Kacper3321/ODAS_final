from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from . import db
from .models import UserSensitiveData
from dotenv import load_dotenv
from os import environ
from .encryptSensData import decrypt_aes

load_dotenv()
aes_key = environ.get('aes_key')
show_sens_data = Blueprint('show_sens_data', __name__)

@show_sens_data.route('/sensitive-data', methods=['GET', 'POST'])
@login_required
def show_sensitive_data():
    if request.method == 'POST':
        auth_code = request.form.get('auth_code')
        user_data = UserSensitiveData.query.filter_by(user_id=current_user.id).first()
        
        if user_data and decrypt_aes(user_data.auth_code,aes_key) == auth_code:  # Sprawdzam czy podany sekret pasuje do sekretu uzytkownika
            card_number = decrypt_aes(user_data.card_number,aes_key)
            document_number = decrypt_aes(user_data.document_number,aes_key)
            return render_template('show_sensitive_data.html', card_number=card_number, document_number=document_number)
        else:
            flash('Invalid authentication code', 'error')

    return render_template('enter_auth_code.html')
