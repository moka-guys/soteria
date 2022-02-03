# app/__init__.py

__doc__=="""Soteria"""
__author__ = "Rachel Duffin"
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Rachel Duffin"
__email__ = "rachel.duffin2@nhs.net"
__status__ = "Production"

import sys
sys.path.append("../")
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.config.from_object("config.Config")
app.app_context().push()
# database
db = SQLAlchemy()

# mail
mail = Mail()

# security
''' 
	Any view using FlaskForm to process the request 
    is already getting CSRF protection. If you have
    views that don't use FlaskForm or make AJAX requests, 
    use the provided CSRF extension to protect those requests as well.
'''
csrf = CSRFProtect()

# login manager
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = "login"
login_manager.refresh_view = 'login'
login_manager.login_message_category = "info"
login_manager.needs_refresh_message = "Session timeout, please re-login"
login_manager.needs_refresh_message_category = "info"


# Initialize Plugins

with app.app_context():

    from app import models, decorators

    db.init_app(app)
    db.create_all()

    login_manager.init_app(app)
    mail.init_app(app)
    from app import views
    csrf.init_app(app)