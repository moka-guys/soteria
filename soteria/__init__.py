#!/usr/bin/env python

__doc__=="""Soteria"""
__author__ = "David Brawand"
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "David Brawand"
__email__ = "dbrawand@nhs.net"
__status__ = "Development"

import os
import sys
sys.path.append("..")
from flask import Flask, render_template, request, redirect
from werkzeug.utils import secure_filename
from config import DevelopmentConfig

app = Flask(__name__)
app.config.from_object(DevelopmentConfig())

from . import views
