from flask import jsonify
from flask_restful import Resource, reqparse, abort, marshal_with, fields
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    get_jwt_identity, set_access_cookies, unset_jwt_cookies,
    get_jwt, jwt_required
)
from web.models import User, Role, RoleName, RevokedToken


parser = reqparse.RequestParser()
_empty_msg = 'cannot be empty'
parser.add_argument('username', type=str, required=True, help=f'Username {_empty_msg}')
parser.add_argument('password', type=str, required=True, help=f'Password {_empty_msg}')
parser.add_argument('email', type=str)


class UserRegister(Resource):
    def post(self):
        data = parser.parse_args()

        if User.find_by_username(data['username']):
            return abort(400, message='This username is already registered')
        
        user = User(username=data['username'], email=data.get('email'),
                    created_at=data.get('created_at'))

        user.set_password(data['password'])
        
        role_type = RoleName.registered_user
        role = Role.find_by_name(role_type)
        if role:
            user.roles.append(role) 

        try:
            user.save_to_db()
            access_token = create_access_token(identity=data['username'])
            refresh_token = create_refresh_token(identity=data['username'])
            response = jsonify({
                'message': f'User {data["username"]} was created',
                'access_token': access_token,
                'refresh_token': refresh_token
            })
            return response
        except:
            return abort(500, message='Something went wrong')

    
class UserLogin(Resource):
    def post(self):
        parser_copy = parser.copy()
        parser_copy.replace_argument('username', required=False)
        
        data = parser_copy.parse_args()
        
        user = User.find_by_username(data['username']) if 'username' in data else\
                User.find_by_email(data['email'])
        
        if not user:
            return abort(400, message='Pass username or email')
        
        if user.check_password(data['password']):
            access_token = create_access_token(identity=data['username'])
            refresh_token = create_refresh_token(identity=data['username'])
            response =  jsonify({
                'message': f'Logged in as {data["username"]}',
                'access_token': access_token,
                'refresh_token': refresh_token
            })
            return response
        else:
            return abort(400, message='Wrong password')


class UserLogout(Resource):
    @jwt_required()
    def delete(self):
        jti = get_jwt()["jti"]
        try:
            revoked_token = RevokedToken(jti=jti)
            revoked_token.add()
            return jsonify({'message': 'Access token has been revoked'})
        except:
            return {'message': 'Something went wrong'}, 500


class TokenRefresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        identity = get_jwt_identity()
        access_token = create_access_token(identity=identity)
        return jsonify(access_token=access_token)


# mock for test protected resource with jwt
class SecretResource(Resource):
    @jwt_required()
    def get(self):
        return {
            'answer': 42
        }
