class Config(object):
    TEST=True
    if TEST:
        DEBUG = True
        SS_DIR = '/usr/local/src/mokaguys/development_area/soteria/samplesheets/'
    else:
        DEBUG = False

    SQLALCHEMY_DATABASE_URI = "sqlite:///database.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    AUTOMATED_SCRIPTS = '/usr/local/src/mokaguys/apps/automate_demultiplex/'

    SESSION_TYPE = 'sqlalchemy'