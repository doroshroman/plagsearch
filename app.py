from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from config import Config


app = Flask(__name__)
app.config.from_object(Config)

api = Api(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from web.resources.user import UserRegister

api.add_resource(UserRegister, '/register')