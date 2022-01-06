from datetime import timedelta

class Config(object):
    SQLALCHEMY_DATABASE_URI = "sqlite:///database.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    AUTOMATED_SCRIPTS = '/usr/local/src/mokaguys/apps/automate_demultiplex/'

    SESSION_TYPE = 'sqlalchemy'
    # set the app so it logs a user out x minutes after the last request was made
    PERMANENT_SESSION_LIFETIME = timedelta(minutes = 5)

    # in test mode the app is run as a normal flask app
    # in production mode the app is run within a docker container
    TEST=True
    if TEST:
        DEBUG = True
        SS_DIR = '/usr/local/src/mokaguys/development_area/soteria/samplesheets/'
    else:
        DEBUG = False

