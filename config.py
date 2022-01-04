class Config(object):
    MAX_CONTENT_LENGTH = 102400000
    UPLOAD_EXTENSIONS = ['.jpg', '.png', '.gif','.csv']
    SS_DIR = '/usr/local/src/mokaguys/development_area/soteria/samplesheets/'
    AUTOMATED_SCRIPTS = '/usr/local/src/mokaguys/apps/automate_demultiplex/'
    SECRET_KEY = 'random key'
    TEST = True

class DevelopmentConfig(Config):
    DEBUG = True
    JSONIFY_PRETTYPRINT_REGULAR = True

class ProductionConfig(Config):
    DEBUG = False