import json
from web3 import Web3, HTTPProvider
from web3.contract import ConciseContract

w3 = Web3(HTTPProvider("http://127.0.0.1:8545"))
print(w3.isConnected())

# default account
private_key = '0x0bb565fc386a4283e484b5cbb750feae0932a0aab577489dc8ca8d792bbee694' # NEED TO CHANGE LATER
account = w3.eth.account.privateKeyToAccount(private_key)

# read compiled contract
truffle_file = json.load(open('./build/contracts/saver.json'))
abi = truffle_file['abi']
bytecode = truffle_file['bytecode']
contract = w3.eth.contract(bytecode=bytecode, abi=abi)

# build transaction
build_tx = contract.constructor().buildTransaction({
    'from': account.address,
    'nonce': w3.eth.getTransactionCount(account.address),
    'gas': 1728712,
    'gasPrice': w3.toWei('21', 'gwei')
})

signed = account.sign_transaction(build_tx)
tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)

tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
contract_address = tx_receipt['contractAddress']

# dump contract address and abi
with open('contract.json', 'w') as out:
    data = {
        "abi": abi,
        "contract_address": contract_address
    }
    json.dump(data, out, indent=4, sort_keys=True)