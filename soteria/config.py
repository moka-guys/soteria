
class Config(object):
    MAX_CONTENT_LENGTH = 102400000
    UPLOAD_EXTENSIONS = ['.jpg', '.png', '.gif','.csv']
    UPLOAD_PATH = 'uploads/'
    LIVE_PASSED_PATH = '/media/data3/share/samplesheet/'
    TEST_PASSED_PATH = "passed/"
    APPLICATION_ROOT = '/usr/local/src/mokaguys/development_area/soteria/'
    SECRET_KEY = 'random key'
    TEST = True

class DevelopmentConfig(Config):
    DEBUG = True
    JSONIFY_PRETTYPRINT_REGULAR = True

class ProductionConfig(Config):
    DEBUG = False