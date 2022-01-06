from soteria import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = "user"

    UserID = db.Column(db.Integer, primary_key=True)
    FirstName=db.Column(db.String(80), unique=True, nullable=False)
    Surname=db.Column(db.String(80), unique=True, nullable=False)
    Email = db.Column(db.String(120), unique=True, nullable=False)
    PHash = db.Column(db.String(300), nullable=False, unique=True)
    CreatedDateTime = db.Column(db.DateTime, server_default=db.func.now())

    def get_id(self):
        return (self.UserID)

class Logins(db.Model):
    __tablename__ = "user_logins"

    LoginID = db.Column(db.Integer, primary_key=True)
    UserID = db.Column(db.Integer, unique=False, nullable=False)
    UserEmail = db.Column(db.String(120), unique=False, nullable=False)
    DateStamp = db.Column(db.DateTime, server_default=db.func.now())

    def get_id(self):
        return (self.LoginID)

class FileUpload(db.Model):
    __tablename__ = "file_upload"

    FileID = db.Column(db.Integer, primary_key=True)
    UserID = db.Column(db.Integer, unique=False, nullable=False)
    UserEmail = db.Column(db.String(120), unique=False, nullable=False)
    DateStamp = db.Column(db.DateTime, server_default=db.func.now())

    def get_id(self):
        return (self.FileID)
    FilePath = db.Column(db.String(120), unique=True, nullable=False)