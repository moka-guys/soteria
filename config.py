import os
from datetime import timedelta

class Config(object):
    # Browsers will only send cookies with requests over HTTPS if the cookie is marked “secure”
    # SESSION_COOKIE_SECURE = True

    DEBUG=False

    # Enable protection agains *Cross-site Request Forgery (CSRF)*
    WTF_CSRF_ENABLED = True

    # set document root as 2 levels up from this file
    DOCUMENT_ROOT = "/".join(os.path.dirname(os.path.realpath(__file__)).split("/")[:-2])

    SS_DIR = '{}/development_area/soteria/samplesheets/'.format(DOCUMENT_ROOT)

    # set locations for secret keys/usernames/passwords/other repos needed by the app
    AMAZON_USERNAME_FILE = "{}/.amazon_email_username".format(DOCUMENT_ROOT)
    AMAZON_PW_FILE = "{}/.amazon_email_pw".format(DOCUMENT_ROOT)
    SOTERIA_SECRETKEYS = "{}/.soteria_secretkeys".format(DOCUMENT_ROOT)
    AUTOMATED_SCRIPTS = '{}/apps/automate_demultiplex/'.format(DOCUMENT_ROOT)

    ''' 
    	CSRF protection requires a secret key to securely sign the token. 
    	By default this will use the Flask app's SECRET_KEY. 
    	If you'd like to use a separate token you can set WTF_CSRF_SECRET_KEY.
    		https://flask-wtf.readthedocs.io/en/stable/csrf.html
    '''
    # get soteria secret keys
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

    # set the app to log out user x minutes after the last request was made
    PERMANENT_SESSION_LIFETIME = timedelta(minutes = 5)