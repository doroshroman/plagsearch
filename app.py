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

from flask_cors import CORS


app = Flask(__name__)
app.config.from_object(Config)

api = Api(app)
cors = CORS(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

jwt = JWTManager(app)

from web.resources.user import ( 
    UserRegister, UserLogin, SecretResource, UserLogout, TokenRefresh, UserLoginWithGoogle
)
from web.resources.document import NewDocument, OneDocument, DocumentAnalyzer

from web.models import RevokedToken

api.add_resource(UserRegister, '/register')
api.add_resource(UserLogin, '/login')
api.add_resource(UserLogout, '/logout')
api.add_resource(TokenRefresh, '/refresh')
api.add_resource(UserLoginWithGoogle, '/google_login')

api.add_resource(NewDocument, '/document/add')
api.add_resource(OneDocument, '/document/<string:hash>')

api.add_resource(DocumentAnalyzer, '/document/analyze/<string:hash>')
api.add_resource(SecretResource, '/secret') # for test purpose


@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    return RevokedToken.is_jti_blacklisted(jti)