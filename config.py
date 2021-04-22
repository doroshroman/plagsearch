import os
import sys
from datetime import timedelta


basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'diploma-is-not-the-best'
    DOCUMENTS_NUMBER_DEFAULT = sys.maxsize
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'hello-friend'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)