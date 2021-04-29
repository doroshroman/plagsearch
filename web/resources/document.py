from flask import jsonify
from flask_restful import Resource, reqparse, abort, marshal_with, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
import werkzeug

from web.models import Document, DocumentType, User
from web.comparison import TextProcessor
from ..utils import DocumentUploader, DocumentCleaner
from ..utils import Hash

import os, json
from config import Config, basedir

from web3 import Web3, HTTPProvider

w3 = Web3(HTTPProvider('http://127.0.0.1:8545'))


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
        identity = get_jwt_identity()
        user = User.find_by_identity(identity)

        uploader = DocumentUploader(data['attachment'], Hash.sha256(identity))
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


def _search_document(hash):
        document = Document.find_by_hash(hash)
        if not document:
            return abort(400, message='This document does not exist')
        return document

class OneDocument(Resource):
    @jwt_required()
    @marshal_with(resource_fields)
    def get(self, hash):
        document = _search_document(hash)
        return document, 200
    
    @jwt_required()
    def delete(self, hash):
        document = _search_document(hash)

        cleaner = DocumentCleaner(document.path)
        if cleaner.erase():
            document.delete_from_db()
            return {'message': 'Document is deleted'}
        else:
            return abort(500, message='Something went wrong')

    @jwt_required()
    @marshal_with(resource_fields)
    def put(self, hash):
        document = _search_document(hash)
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
    #@jwt_required()
    def post(self, hash):
        document = _search_document(hash)
        
        # normalize text for simhash
        processor = TextProcessor(document.path)
        simhash = Hash.simhash(processor.normalize())
        
        contract_path = os.path.join(basedir, os.path.join('blockchain', 'contract.json'))
        with open(contract_path, 'r') as in_:
            contract_data = json.load(in_)  

        key="0x0bb565fc386a4283e484b5cbb750feae0932a0aab577489dc8ca8d792bbee694" #change later
        account = w3.eth.account.privateKeyToAccount(key)
        account_address= account.address

        abi = contract_data['abi']
        contract_address = contract_data['contract_address']

        # create contract instance
        saver = w3.eth.contract(
            address=contract_address, abi=abi
        )
        tx = saver.functions.addHash(simhash).buildTransaction({'nonce': w3.eth.getTransactionCount(account_address)})
        signed_tx = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        w3.eth.wait_for_transaction_receipt(tx_hash)
        
        all_hashes = saver.functions.getAllHashes().call()
        print(all_hashes)
        return 200


class DocumentList(Resource):
    @jwt_required()
    @marshal_with(resource_fields)
    def get(self):
        identity = get_jwt_identity()
        user = User.find_by_identity(identity)
        documents = user.documents.all()

        return documents, 200