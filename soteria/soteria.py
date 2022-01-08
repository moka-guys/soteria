#!/usr/bin/env python

__doc__=="""Soteria"""
__author__ = "Rachel Duffin"
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Rachel Duffin"
__email__ = "rachel.duffin2@nhs.net"
__status__ = "Development"

import sys
sys.path.append("../")
from flask import Flask
sys.path.append("..")
from config import Config
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail

# create flask login instance
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = "login"
login_manager.refresh_view = 'login'
login_manager.login_message_category = "info"
login_manager.needs_refresh_message = "Session timeout, please re-login"
login_manager.needs_refresh_message_category = "info"

db = SQLAlchemy()
mail = Mail()

def create_app():
    """
    Create the app within a function for ease of use
    """

    # create SQLAlchemy, Migrate and Bycrypt instances
    migrate = Migrate()

    app = Flask(__name__)

    # Import app configuration
    app.config.from_object(Config())

    # Initialize Plugins
    login_manager.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    return app