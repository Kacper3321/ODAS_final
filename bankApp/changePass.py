from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from . import db
from flask_bcrypt import generate_password_hash, check_password_hash
from .models import User
import math


change_pass = Blueprint('change_pass', __name__)

@change_pass.route("/change-password", methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        #pobranie danych z formularza
        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        confirm_new_password = request.form.get("confirm_new_password")

        #wyliczenie entropii hasla i sprawdzenie czy jest wystarczajaco silne
        is_strong, message = is_password_strong(new_password)
        if not is_strong:
            flash(message, 'error')
        else:
            flash(message, 'success')
            user = User.query.get(current_user.id)
            if not check_password_hash(user.password, current_password):    # sprawdzanie podanego hasla
                flash('Given password is invalid.', 'error')
            elif new_password != confirm_new_password:                      # sprawdzenie spojnosci nowego hasla z potwierdzeniem
                flash('New password doesn\'t match Confirm Password.', 'error')
            else:         
                #aktualizuje haslo w bazie danych                                                  
                user.password = generate_password_hash(new_password)
                user.password_length = len(new_password)
                #tworze czesciowe hasla na podstawie nowego hasla
                create_database_for_partial_passwords(current_user.id, new_password)
                db.session.commit()
                flash('Your password has been updated.', 'success')
                return redirect(url_for('views.home'))    
    return render_template("change_password.html")



def create_database_for_partial_passwords(id, string):
    from .models import User, HashedPasswd
    from flask_bcrypt import generate_password_hash
    from . import db

    n = len(string)
    user = User.query.get(id)
    if not user:
        flash('Your password has been updated.', 'success')
        return

    #mozliwe maski hasla
    combinations = []
    if n == 8:
        combinations = [(0, 3, 6), (1, 4, 7), (0, 2, 5), (2, 5, 7)]
    elif n == 9:
        combinations = [(0, 2, 4, 6),(1, 3, 5, 7),(2, 4, 6, 8),(0, 3, 5, 8)]
    elif n == 10:
        combinations = [(0, 2, 5, 7),(1, 3, 6, 8),(2, 4, 7, 9),(0, 3, 6, 9)]
    elif n == 11:
        combinations = [(0, 2, 4, 6, 8),(1, 3, 5, 7, 9),(0, 2, 5, 7, 10),(1, 3, 6, 8, 10)]
    elif n == 12:
        combinations = [(0, 2, 4, 6, 8),(1, 3, 5, 7, 9),(0, 3, 6, 9, 11),(2, 5, 8, 10, 11)]

    HashedPasswd.query.filter_by(user_id=user.id).delete()

    for combo in combinations:
        mask = ''.join(str(index) for index in combo)
        pass_for_mask = ''.join(string[index] for index in combo)
        hashed_passwd = generate_password_hash(pass_for_mask)

        new_partial_pass = HashedPasswd(user_id=user.id, hashed_passwd=hashed_passwd, indexes=mask)
        db.session.add(new_partial_pass)

    db.session.commit()


def calculate_entropy(password):
    if not password:
        return 0
    charset_size = len(set(password))  # wyliczam dlugosc zbioru unikalnych znakow hasla
    entropy = len(password) * math.log2(charset_size)
    return entropy

import re

def is_password_strong(password):
    if len(password) < 8:
        return False, "Password is too short"
    if not re.search(r"[A-Z]", password):
        return False, "Password must include at least one uppercase letter"
    if not re.search(r"[a-z]", password):
        return False, "Password must include at least one lowercase letter"
    if not re.search(r"[0-9]", password):
        return False, "Password must include at least one digit"
    if not re.search(r"[!@#$%&*?]", password):
        return False, "Password must include at least one special character"
    if len(set(password)) < 4:
        return False, "Password must have more than 3 unique characters"
    
    entropy = calculate_entropy(password)
    if entropy < 30:  # jezeli entropia jest mniejsza niz 30 uznaje haslo jako za slabe
        return False, "Password is too weak"

    return True, "Password is strong"