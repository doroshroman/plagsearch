from config import Config
import os
from werkzeug.utils import secure_filename
import pathlib
import hashlib
from hashes.simhash import simhash


class DuplicateNameException(Exception):
    pass


class DocumentUploader:
    def __init__(self, document, username):
        self.data = document
        self.filename = self.data.filename
        self.username = username
        self._create_proper_directory()

    def _create_proper_directory(self):
        pathlib.Path(os.path.join(Config.UPLOAD_FOLDER, f'{self.username}'))\
                .mkdir(parents=True, exist_ok=True)

    def allowed_file(self):
        return '.' in self.filename and \
            self.filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS
    
    def upload(self):
        if self.data and self.allowed_file():
            doc_name = os.path.join(f'{self.username}', secure_filename(self.filename))

            doc_path = os.path.join(Config.UPLOAD_FOLDER, doc_name)
            if os.path.isfile(doc_path):
                raise DuplicateNameException()

            self.data.save(doc_path)
            return (self.filename, doc_path) if os.path.isfile(doc_path) else None
                
        return None


class DocumentCleaner:
    def __init__(self, path):
        self.path = path
    
    def erase(self):
        if os.path.isfile(self.path):
            os.remove(self.path)

        return not os.path.isfile(self.path)

class Hash:
    def __init__(self, message):
        self.message = message
    
    def sha256(self):
        return hashlib.sha256(message.encode()).hexdigest()
    
    def simhash(self):
        return simhash(self.message).hex()
    