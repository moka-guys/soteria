
class Config(object):
    MAX_CONTENT_LENGTH = 102400000
    UPLOAD_EXTENSIONS = ['.jpg', '.png', '.gif','.csv']
    UPLOAD_PATH = 'uploads'
    APPLICATION_ROOT = '/'


class DevelopmentConfig(Config):
    DEBUG = True
    JSONIFY_PRETTYPRINT_REGULAR = True

class ProductionConfig(Config):
    DEBUG = False