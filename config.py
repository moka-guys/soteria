import os
from datetime import timedelta

class Config(object):
    # in test mode the app is run as a normal flask app
    # in production mode the app is run within a docker container
    TEST=True

    if TEST:
        DEBUG = True
        SS_DIR = '/usr/local/src/mokaguys/development_area/soteria/samplesheets/'
    else:
        DEBUG = False
        SS_DIR = ''

    # set document root as 2 levels up from this file
    DOCUMENT_ROOT = "/".join(os.path.dirname(os.path.realpath(__file__)).split("/")[:-2])
    # set locations for secret keys/usernames/passwords/other repos needed by the app
    AMAZON_USERNAME_FILE = "{}/.amazon_email_username".format(DOCUMENT_ROOT)
    AMAZON_PW_FILE = "{}/.amazon_email_pw".format(DOCUMENT_ROOT)
    SOTERIA_SECRETKEYS = "{}/.soteria_secretkeys".format(DOCUMENT_ROOT)
    AUTOMATED_SCRIPTS = '{}/apps/automate_demultiplex/'.format(DOCUMENT_ROOT)

    # Import soteria hidden keys
    with open(SOTERIA_SECRETKEYS, "r") as keys:
        for line in keys.readlines():
            if "MAIN_SECRET_KEY" in line:
                SECRET_KEY = line.split('\'')[1]
            elif "WTF_CSRF_SECRET_KEY" in line:
                WTF_CSRF_SECRET_KEY = line.split('\'')[1]
            elif "SECURITY_PASSWORD_SALT" in line:
                SECURITY_PASSWORD_SALT = line.split('\'')[1]

    # set smtp server password and username
    with open(AMAZON_USERNAME_FILE, "r") as email_username_file:
        MAIL_USERNAME = email_username_file.readline().rstrip()
    with open(AMAZON_PW_FILE, "r") as email_password_file:
        MAIL_PASSWORD = email_password_file.readline().rstrip()

    # Mail server settings
    MAIL_SERVER = "email-smtp.eu-west-1.amazonaws.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True

    SQLALCHEMY_DATABASE_URI = "sqlite:///database.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SESSION_TYPE = 'sqlalchemy'

    # set the app so it logs a user out x minutes after the last request was made
    PERMANENT_SESSION_LIFETIME = timedelta(minutes = 5)

