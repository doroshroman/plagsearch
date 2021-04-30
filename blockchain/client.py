import json
from deploy import w3
from dotenv import load_dotenv
import os

load_dotenv()

PRIVATE_KEY = os.environ.get('PRIVATE_KEY')

basedir = os.path.abspath(os.path.dirname(__file__))

class Client:
    def __init__(self):
        self.contract_data = json.load(open(os.path.join(basedir, './contract.json')))
        self.account = w3.eth.account.privateKeyToAccount(PRIVATE_KEY)

        self.saver = w3.eth.contract(
            address=self.contract_data['contract_address'],
            abi=self.contract_data['abi']
        )

    def add(self, value):
        tx = self.saver.functions.addHash(value).buildTransaction(
            {
                'nonce': w3.eth.getTransactionCount(self.account.address)
            }
        )
        signed_tx = self.account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        w3.eth.wait_for_transaction_receipt(tx_hash)

    def get_all(self):
        return self.saver.functions.getAllHashes().call()

