# soteria/soteria.py

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
from config import Config
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from flask_talisman import Talisman

# create database, mail and migrate objects
db = SQLAlchemy()
mail = Mail()
migrate = Migrate()
login_manager = LoginManager()
login_manager = LoginManager()

login_manager.session_protection = 'strong'
login_manager.login_view = "login"
login_manager.refresh_view = 'login'
login_manager.login_message_category = "info"
login_manager.needs_refresh_message = "Session timeout, please re-login"
login_manager.needs_refresh_message_category = "info"

def create_app():
    """
    Create the app within a function for ease of use
    """
    app = Flask(__name__)
    # default content security policy is strict and prevents loading any resources that are not in the same domain as
    # the application. Add allowed sites (bootstrap and self, and unsafe-inline (allows inline scripts))
    csp = {'default-src': [
        '\'self\'',
        '\'unsafe-inline\'',
        'ajax.googleapis.com',
        'cdnjs.cloudflare.com',
        'maxcdn.bootstrapcdn.com'
    ]}

    Talisman(app, content_security_policy=csp)
    # Import app configuration
    app.config.from_object(Config())

    # Initialize Plugins
    login_manager.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    return app