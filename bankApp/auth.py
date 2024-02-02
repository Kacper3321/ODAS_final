from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from . import db
from .models import User, HashedPasswd
from flask_login import login_user, logout_user, login_required, current_user
from flask_bcrypt import check_password_hash
import random
import time

auth = Blueprint("auth", __name__)

@auth.route("/login", methods=['GET', 'POST'])
def login():

    #Jezeli jestem juz zalogowany przeniesie mnie do strony domowej
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))
    user = None
    enabled_indexes = []
    password_length = 0

    if request.method == 'POST':
        # Inicjalizacja licznika prób logowania i opóźnienia, jeśli nie istnieją
        session.setdefault('login_attempts', 0)
        session.setdefault('login_delay_until', 0)
        session.setdefault('failed_login_series', 0)
        

        # Sprawdzenie, czy nie jest za wcześnie na kolejną próbę logowania
        if time.time() < session['login_delay_until']:
            remaining_delay = int(session['login_delay_until'] - time.time())
            flash(f'Too many failed login attempts. Please wait {remaining_delay} seconds.', category='error')
            return render_template("login.html", user=user, enabled_indexes=enabled_indexes, password_length=password_length)
        elif session['login_attempts'] == 2:
            # Resetuj licznik prób logowania po upływie blokady
            session['login_attempts'] = 0


        if 'account_number' in request.form:
            account_number = request.form.get("account_number")
            user = User.query.filter_by(account_number=account_number).first()
            if user:
                if user.activated:
                    password_length = user.password_length
                    predefined_combinations = {
                        8: [(0, 3, 6), (1, 4, 7), (0, 2, 5), (2, 5, 7)],
                        9: [(0, 2, 4, 6),(1, 3, 5, 7),(2, 4, 6, 8),(0, 3, 5, 8)],
                        10: [(0, 2, 5, 7),(1, 3, 6, 8),(2, 4, 7, 9),(0, 3, 6, 9)],
                        11: [(0, 2, 4, 6, 8),(1, 3, 5, 7, 9),(0, 2, 5, 7, 10),(1, 3, 6, 8, 10)],
                        12: [(0, 2, 4, 6, 8),(1, 3, 5, 7, 9),(0, 3, 6, 9, 11),(2, 5, 8, 10, 11)]
                    }
                    #zabezpieczam sie na wypadek jakby bylo jakies haslo z niedozwolona dlugoscia
                    if password_length in predefined_combinations:
                        #wybieram ten zestaw masek dla dlugosci mojego hasla i wybieram z nich losowa
                        combination_set = predefined_combinations[password_length]
                        selected_combination = random.choice(combination_set)
                        session['enabled_indexes'] = list(selected_combination)
                    else:
                        # Handle unexpected password length
                        flash('Unexpected password length.', category='error')
                        enabled_indexes = []
                    session['user_id'] = user.id
                else: 
                    flash('Account has been blocked. Contact your bank.', category='error')
            else:
                flash('Account does not exist.', category='error')
        #formularz podawania hasla
        elif 'partial_password' in request.form:
            user_id = session.get('user_id')
            enabled_indexes = session.get('enabled_indexes', [])
            enabled_indexes.sort()

            if user_id and enabled_indexes:
                user = User.query.filter_by(id=user_id).first()
                dynamic_fields = [request.form.get(f"field{i}") for i in enabled_indexes]
                indexes = ''.join(str(i) for i in enabled_indexes)
                givenPartialPass = ''.join(dynamic_fields)
                partialPass = HashedPasswd.query.filter_by(user_id=user_id, indexes=indexes).first()
                
                if partialPass and check_password_hash(partialPass.hashed_passwd, givenPartialPass):
                    # Przy udanym logowaniu zeruje liczniki nieudanych prob
                    session['login_attempts'] = 0
                    session['failed_login_series'] = 0
                    user.login_count += 1
                    db.session.commit()
                    flash("Logged in!", category='success')
                    login_user(user, remember=True)
                    session.pop('user_id', None)
                    session.pop('enabled_indexes', None)
                    return redirect(url_for('views.home'))
                else:
                    # nieudana proba logowania
                    session['login_attempts'] += 1

                    if session['login_attempts'] == 1:
                        if session['failed_login_series'] == 0:
                            flash('Password is incorrect. Another failed attempt will result in a temporary suspension.', category='error')
                        else:
                            flash('Password is incorrect. Another failed attempt will block this account.', category='error')
                    elif session['login_attempts'] >= 2:
                        # Zaznaczam nieudana serie i przygotowuje licznik prob na kolejna
                        session['failed_login_series'] += 1
                        session['login_attempts'] = 0

                        if session['failed_login_series'] >= 2:
                            # Jezeli po 2 seriach nie uda sie zalogowac do aplikacji to zablokuje konto
                            if user:
                                user.activated = False
                                db.session.commit()
                            session['failed_login_series'] = 0
                            flash('Account has been blocked due to repeated failed login attempts.', category='error')
                            return redirect(url_for('auth.login'))
                        else:
                            # ustawienie opoznienia przed ponowna sesja prob logowania
                            delay_seconds = 10  # wartosc w sekundach
                            session['login_delay_until'] = time.time() + delay_seconds
                            flash('Too many failed login attempts. Your account will be locked for 10 seconds.', category='error')
                    
                    session.pop('user_id', None)
                    session.pop('enabled_indexes', None)
                    user = None
            else:
                flash("Session expired or invalid request.", category='error')

    # Pobieranie enabled_indexes z sesji, jeśli istnieją
    enabled_indexes = session.get('enabled_indexes', [])
    return render_template("login.html", user=user, enabled_indexes=enabled_indexes, password_length=password_length)

@auth.route("/logout")
@login_required
def logout():
    session['login_attempts'] = 0
    session['login_delay_until'] = 0
    logout_user()
    return redirect(url_for("views.home"))
