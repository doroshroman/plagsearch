from config import Config
import os
from werkzeug.utils import secure_filename
import pathlib
import hashlib
from hashes.simhash import simhash
from datetime import datetime as dt


class DocumentUploader:
    def __init__(self, document, username):
        self.data = document
        self.username = username
        self.filename = self.data.filename
        self._create_proper_directory()

    def _create_proper_directory(self):
        pathlib.Path(os.path.join(Config.UPLOAD_FOLDER, f'{self.username}'))\
                .mkdir(parents=True, exist_ok=True)

    def allowed_file(self):
        return '.' in self.filename and \
            self.filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS
    
    def upload(self):
        if self.data and self.allowed_file():
            name, ext = self.filename.split('.')
            self.filename = f'{name}_{dt.timestamp(dt.now())}.{ext}'
            doc_name = os.path.join(f'{self.username}', secure_filename(self.filename))

            doc_path = os.path.join(Config.UPLOAD_FOLDER, doc_name)

            self.data.save(doc_path)
            return doc_path if os.path.isfile(doc_path) else None
                
        return None


class DocumentCleaner:
    def __init__(self, path):
        self.path = path
    
    def erase(self):
        if os.path.isfile(self.path):
            os.remove(self.path)

        return not os.path.isfile(self.path)

class Hash:

    @staticmethod
    def sha256(message):
        return hashlib.sha256(message.encode('utf-8')).hexdigest()
    
    @staticmethod
    def simhash(message):
        return simhash(message).hex()
    