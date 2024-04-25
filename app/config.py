import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    TEMPLATE_FOLDER = os.environ.get('TEMPLATE_FOLDER')
    STATIC_FOLDER = os.environ.get('STATIC_FOLDER')
    PERMANENT_SESSION_LIFETIME = timedelta(days=365)
    print(TEMPLATE_FOLDER)
    TEMPLATES_AUTO_RELOAD = True
    DEBUG = False
    TESTING = False


class ProductionConfig(Config):
    pass


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
