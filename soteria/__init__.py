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
sys.path.append("..")
from flask import Flask, render_template, request, redirect
from werkzeug.utils import secure_filename
from config import DevelopmentConfig
from flask_login import LoginManager

login_manager = LoginManager()
login_manager.session_protection = 'strong'
app = Flask(__name__)
app.config.from_object(DevelopmentConfig())
login_manager.init_app(app)

from . import views

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id) # Fetch the user from the database