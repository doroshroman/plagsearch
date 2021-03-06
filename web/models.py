from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from enum import Enum
from config import Config
from datetime import datetime as dt
import os


users_roles = db.Table('users_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True)
)

class RoleName(Enum):
    registered_user = 'Registered User'
    registered_with_google = 'Registered User With Google'


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
    documents = db.relationship('Document', backref='user', lazy='dynamic')

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
    
    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email).first()
    
    @classmethod
    def find_by_identity(cls, identity):
        by_username = cls.find_by_username(identity)
        by_email = cls.find_by_email(identity)
        return by_username if by_username else by_email

    def __repr__(self):
        return f'User {self.id}: {self.username}, {self.email}'
    

class RevokedToken(db.Model):
    __tablename__ = 'revoked_tokens'
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(120))
    
    def add(self):
        db.session.add(self)
        db.session.commit()
    
    @classmethod
    def is_jti_blacklisted(cls, jti):
        query = cls.query.filter_by(jti = jti).first()
        return bool(query)


class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True, nullable=False)
    path = db.Column(db.String, index=True, nullable=False)
    description = db.Column(db.String, nullable=True)
    hash_sha256 = db.Column(db.String(65), nullable=True)
    simhash = db.Column(db.String, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    doc_type = db.Column(db.Integer, db.ForeignKey('document_type.id'), nullable=True)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
    
    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
    
    @classmethod
    def find_by_hash(cls, hash):
        return cls.query.filter_by(hash_sha256=hash).first()


class DocumentType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True, nullable=False)
    description = db.Column(db.String(256), index=True)