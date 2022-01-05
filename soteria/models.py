from soteria import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    firstname=db.Column(db.String(80), unique=True, nullable=False)
    surname=db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    pwd = db.Column(db.String(300), nullable=False, unique=True)
    created_on = db.Column(db.DateTime, server_default=db.func.now())

class Logins(db.Model):
    __tablename__ = "user_logins"

    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(120), unique=False, nullable=False)
    datestamp = db.Column(db.DateTime, server_default=db.func.now())

class File_upload(db.Model):
    __tablename__ = "file_upload"

    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(120), unique=False, nullable=False)
    file = db.Column(db.String(120), unique=True, nullable=False)