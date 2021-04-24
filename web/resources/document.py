from flask import jsonify
from flask_restful import Resource, reqparse, abort, marshal_with, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
import werkzeug

from web.models import Document, DocumentType, User

from ..utils import DocumentUploader, DocumentCleaner
from ..utils import DuplicateNameException
from ..utils import Hash
import os
from config import Config


parser = reqparse.RequestParser()
_empty_msg = 'cannot be empty'
parser.add_argument('description', type=str)
parser.add_argument('attachment', type=werkzeug.datastructures.FileStorage, location='files',
                     required=True, help=f'Attachment field {_empty_msg}')


class IdItem(fields.Raw):
    def format(self, value):
        return value.id


resource_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'description': fields.String,
    'hash_sha256': fields.String,
    'simhash': fields.String,
    'user': IdItem,
    'doc_type': IdItem
}


class NewDocument(Resource):
    @jwt_required()
    def post(self):
        data = parser.parse_args()
        username = get_jwt_identity()
        user = User.find_by_username(username)

        uploader = DocumentUploader(data['attachment'], username)
        try:
            file_name, path = uploader.upload()

            if path:
                document = Document(
                    name=file_name, path=path, description=data['description'],
                    user=user
                    )
                document.save_to_db()

                return {'message': f'{file_name} is successfully created'}
            else:
                return abort(400, message=f'Incorrect document extension')

        except DuplicateNameException:
            return abort(400, message=f'This document is already exists')
        except Exception:
            return abort(500, message='Something went wrong')


def _find_document(username, name):
    path = os.path.join(Config.UPLOAD_FOLDER, os.path.join(username, name))
    doc = Document.find_by_path(path)
    if not doc:
        return abort(400, message='Document is not exists')
    return doc


class OneDocument(Resource):
    @jwt_required()
    @marshal_with(resource_fields)
    def get(self, name):
        username = get_jwt_identity()
        doc = _find_document(username, name)
        return doc, 200
    
    @jwt_required()
    def delete(self, name):
        username = get_jwt_identity()
        doc = _find_document(username, name)
        
        
        cleaner = DocumentCleaner(doc.path)
        if cleaner.erase():
            doc.delete_from_db()

        return {'message': 'Document is deleted'}
        
    @jwt_required()
    def put(self, name):
        username = get_jwt_identity()
        
