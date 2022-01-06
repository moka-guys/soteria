#!/usr/bin/env python

__doc__=="""Soteria"""
__author__ = "Rachel Duffin"
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Rachel Duffin"
__email__ = "rachel.duffin2@nhs.net"
__status__ = "Development"

import os
import sys
sys.path.append("../")
from flask import Flask, render_template, request, redirect
from werkzeug.utils import secure_filename
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

    # Import soteria hidden keys
    with open(app.config['SOTERIA_SECRETKEYS'], "r") as keys:
        for line in keys.readlines():
            if "MAIN_SECRET_KEY" in line:
                app.config['SECRET_KEY'] = line.split('\'')[1]
            elif "WTF_CSRF_SECRET_KEY" in line:
                app.config['WTF_CSRF_SECRET_KEY'] = line.split('\'')[1]
            elif "SECURITY_PASSWORD_SALT" in line:
                app.config['SECURITY_PASSWORD_SALT'] = line.split('\'')[1]

    # set smtp server password and username
    with open(app.config['AMAZON_USERNAME_FILE'], "r") as email_username_file:
        app.config['MAIL_USERNAME'] = email_username_file.readline().rstrip()
    with open(app.config['AMAZON_PW_FILE'], "r") as email_password_file:
        app.config['MAIL_PASSWORD'] = email_password_file.readline().rstrip()

    # Initialize Plugins
    login_manager.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    return app