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

# create flask login instance
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = "login"
login_manager.login_message_category = "info"

db = SQLAlchemy()

def create_app():
    """
    Create the app within a function for ease of use
    """

    # create SQLAlchemy, Migrate and Bycrypt instances
    migrate = Migrate()

    app = Flask(__name__)

    # Import app configuration
    app.config.from_object(Config())

    # Import hidden keys
    script_dir = os.path.dirname(__file__)
    secret_key_relpath = "../.secretkeys"
    secret_key_abspath = os.path.join(script_dir, secret_key_relpath)

    with open(secret_key_abspath, "r") as keys:
        for line in keys.readlines():
            if "MAIN_SECRET_KEY" in line:
                app.config['SECRET_KEY'] = line.split('\'')[1]
            elif "WTF_CSRF_SECRET_KEY" in line:
                app.config['WTF_CSRF_SECRET_KEY'] = line.split('\'')[1]

    # Initialize Plugins
    login_manager.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)

    return app