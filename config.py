
class Config(object):
    MAX_CONTENT_LENGTH = 102400000
    UPLOAD_EXTENSIONS = ['.jpg', '.png', '.gif','.csv']
    SS_DIR = '/soteria/samplesheets/'
    AUTOMATED_SCRIPTS = '/soteria/automate_demultiplex/'
    SECRET_KEY = 'random key'
    TEST = True

class DevelopmentConfig(Config):
    DEBUG = True
    JSONIFY_PRETTYPRINT_REGULAR = True

class ProductionConfig(Config):
    DEBUG = False