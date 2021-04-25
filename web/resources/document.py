from flask import jsonify
from flask_restful import Resource, reqparse, abort, marshal_with, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
import werkzeug

from web.models import Document, DocumentType, User

from ..utils import DocumentUploader, DocumentCleaner
from ..utils import Hash

import os
from config import Config


parser = reqparse.RequestParser()
_empty_msg = 'cannot be empty'
parser.add_argument('name', type=str, required=True, help=f'Name field {_empty_msg}')
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
    @marshal_with(resource_fields)
    def post(self):
        data = parser.parse_args()
        username = get_jwt_identity()
        user = User.find_by_username(username)

        uploader = DocumentUploader(data['attachment'], username)
        try:
            path = uploader.upload()

            if path:
                hash_sha256 = Hash.sha256(path)

                document = Document(
                    name=data['name'], path=path, description=data['description'],
                    hash_sha256=hash_sha256, user=user
                    )
                document.save_to_db()

                return document, 200
            else:
                return abort(400, message=f'Incorrect document extension')

        except Exception:
            return abort(500, message='Something went wrong')


class OneDocument(Resource):
    def _search_document(self, hash):
        document = Document.find_by_hash(hash)
        if not document:
            return abort(400, message='This document does not exist')
        return document

    @jwt_required()
    @marshal_with(resource_fields)
    def get(self, hash):
        document = self._search_document(hash)
        return document, 200
    
    @jwt_required()
    def delete(self, hash):
        document = self._search_document(hash)

        cleaner = DocumentCleaner(document.path)
        if cleaner.erase():
            document.delete_from_db()
            return {'message': 'Document is deleted'}
        else:
            return abort(500, message='Something went wrong')

    @jwt_required()
    @marshal_with(resource_fields)
    def put(self, hash):
        document = self._search_document(hash)
        parser_copy = parser.copy()
        parser_copy.remove_argument('attachment')

        data = parser_copy.parse_args()
        name, description = data['name'], data['description']
        document.name = name

        if description:
            document.description = description
        
        try:
            document.save_to_db()
            return document, 200
        except:
            return abort(500, message='Something went wrong')


class DocumentAnalyzer(Resource):
    @jwt_required()
    def post(self, id):
        pass
