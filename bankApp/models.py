from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

#UserMixin pozwala na uzytkowanie 
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    account_number = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    balance = db.Column(db.Integer)
    name = db.Column(db.String(150))
    surname = db.Column(db.String(150))
    password_length = db.Column(db.Integer)
    login_count = db.Column(db.Integer, default=0)
    activated = db.Column(db.Boolean, default=True, nullable=False)

    hashed_passwords = relationship('HashedPasswd', backref='user', lazy=True)
    user_sensitive_data = relationship('UserSensitiveData', backref='user', lazy=True)
    transactions_made = db.relationship('Transactions', foreign_keys='Transactions.payer_id', backref='payer', lazy=True)
    transactions_received = db.relationship('Transactions', foreign_keys='Transactions.recipient_id', backref='recipient', lazy=True)

class HashedPasswd(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    hashed_passwd = db.Column(db.String(150))
    indexes = db.Column(db.String(150))

class UserSensitiveData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    card_number = db.Column(db.String(150))
    document_number = db.Column(db.String(150))
    auth_code = db.Column(db.String(150), unique=True)

class Transactions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer)
    title = db.Column(db.String(150))
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    recipent_name =db.Column(db.String(150))
    recipent_surname = db.Column(db.String(150))
    payer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    payer_name =db.Column(db.String(150))
    payer_surname = db.Column(db.String(150))
