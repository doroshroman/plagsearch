from flask_restful import Resource, reqparse, abort, marshal_with, fields
from web.models import User, Role, RoleName


class RoleItem(fields.Raw):
    def format(self, value):
        return value.name.value

class UserRegister(Resource):
    parser = reqparse.RequestParser()
    _empty_msg = 'cannot be empty'
    parser.add_argument('username', type=str, required=True, help=f'Username {_empty_msg}')
    parser.add_argument('password', type=str, required=True, help=f'Password {_empty_msg}')

    resource_fields = {
        'id': fields.Integer,
        'username': fields.String,
        'email': fields.String,
        'created_at': fields.DateTime(dt_format='rfc822'),
        'roles': fields.List(RoleItem)
    }

    @marshal_with(resource_fields)
    def post(self):
        data = UserRegister.parser.parse_args()

        if User.find_by_username(data['username']):
            return abort(400, message='This username is already registered')
        
        user = User(username=data['username'], email=data.get('email'),
                    created_at=data.get('created_at'))

        user.set_password(data['password'])
        
        role_type = RoleName.registered_user
        role = Role.find_by_name(role_type)
        if role:
            user.roles.append(role) 

        user.save_to_db()

        return user, 200



