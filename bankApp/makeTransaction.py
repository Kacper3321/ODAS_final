from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from . import db
from .models import User, Transactions

makeTransaction = Blueprint('makeTransaction', __name__)

@makeTransaction.route('/make-transaction', methods=['GET', 'POST'])
@login_required
def make_transaction():
    if request.method == 'POST':
        title = request.form.get('title')
        recipient_account = request.form.get('recipient')
        amount = request.form.get('amount', type=int)

        # Sprawdzam czy dane zostay poprawnie podane 
        if not title or not recipient_account or not amount:
            flash('Please fill out all fields', 'error')
            return redirect(url_for('makeTransaction.make_transaction'))
        #uzytkownik nie moze wyslac ujemnych pieniedzy zeby przypadkiem nie doladowal sobie konta
        if amount <= 0 or amount > current_user.balance:
            flash('Invalid transaction amount', 'error')
            return redirect(url_for('makeTransaction.make_transaction'))

        # Sprawdzam czy istnieje taki odbiorca 
        recipient = User.query.filter_by(account_number=recipient_account).first()
        if not recipient:
            flash('Recipient account not found', 'error')
            return redirect(url_for('makeTransaction.make_transaction'))

        #nie zezwalam na wysylanie pieniedzy do samego siebie
        if recipient.account_number == current_user.account_number:
            flash('Cannot send money to yourself', 'error')
            return redirect(url_for('makeTransaction.make_transaction'))

        # tworze nowe wpisy do tabeli transakcji oraz aktualizuje salda nadawcy i odbiorcy
        try:
            new_transaction = Transactions(amount=amount,title=title,recipient_id=recipient.id,payer_id=current_user.id,recipent_name = recipient.name, recipent_surname = recipient.surname,payer_name = current_user.name, payer_surname = current_user.surname)
            db.session.add(new_transaction)
            current_user.balance -= amount
            recipient.balance += amount
            db.session.commit()
            flash('Transaction successful', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Transaction failed', 'error')
            return redirect(url_for('makeTransaction.make_transaction'))

        return redirect(url_for('views.home'))

    return render_template('make_transaction.html', user=current_user)
