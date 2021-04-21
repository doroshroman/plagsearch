from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from enum import Enum
from config import Config
from datetime import datetime as dt


users_roles = db.Table('users_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True)
)

class RoleName(Enum):
    registered_user = 'Registered User'


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Enum(RoleName), default=RoleName.registered_user, nullable=False)
    documents_number = db.Column(db.Integer, default=Config.DOCUMENTS_NUMBER_DEFAULT,
                                 nullable=False)
    users = db.relationship("User",
                            secondary=users_roles,
                            backref='roles')
        
    @classmethod
    def find_by_name(cls, name):
        return cls.query.filter_by(name=name).first()

    def __repr__(self):
        return f'Role: {self.name}, Documents available: {self.documents_number}'


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=dt.utcnow())

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()
    
    def __repr__(self):
        return f'User {self.id}: {self.username}, {self.email}'
