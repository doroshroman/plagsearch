from flask import Flask
from flask_restful import Api

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from flask_jwt_extended import (
    JWTManager, get_jwt, create_access_token,
    set_access_cookies, get_jwt_identity
)

from datetime import datetime
from datetime import timedelta
from datetime import timezone

from config import Config


app = Flask(__name__)
app.config.from_object(Config)

api = Api(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

jwt = JWTManager(app)

from web.resources.user import UserRegister, UserLogin, SecretResource, UserLogout, TokenRefresh

from web.models import RevokedToken

api.add_resource(UserRegister, '/register')
api.add_resource(UserLogin, '/login')
api.add_resource(UserLogout, '/logout')
api.add_resource(TokenRefresh, '/refresh')
api.add_resource(SecretResource, '/secret') # for test purpose

@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    return RevokedToken.is_jti_blacklisted(jti)