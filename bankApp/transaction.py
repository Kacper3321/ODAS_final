from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from . import db
from .models import Transactions

transaction = Blueprint('transaction', __name__)

@transaction.route('/transactions', methods=['GET', 'POST'])
@login_required
def transactions():
    # Pobieranie transakcji wychodzących i przychodzących
    outgoing_transactions = Transactions.query.filter_by(payer_id=current_user.id).all()
    incoming_transactions = Transactions.query.filter_by(recipient_id=current_user.id).all()
    

    return render_template('transactions.html', outgoing_transactions=outgoing_transactions, incoming_transactions=incoming_transactions)

