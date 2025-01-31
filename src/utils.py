# utils.py
from web3 import Web3
from config import RPC_URL, PRIVATE_KEY, WALLET_ADDRESS
import json
import time

# Web3 setup
web3 = Web3(Web3.HTTPProvider(RPC_URL))

if web3.is_connected():
    print(f"Connected to network with wallet: {WALLET_ADDRESS}")
else:
    raise ConnectionError("Failed to connect to the network")

# Get gas price (current gas price * 2)
def get_gas_price():
    base_gas_price = web3.eth.gas_price
    return int(base_gas_price * 3.5)

# Sign and send transaction
def send_transaction(transaction):
    try:
        signed_txn = web3.eth.account.sign_transaction(transaction, PRIVATE_KEY)
        tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
        print(f"Transaction sent with hash: {Web3.to_hex(tx_hash)}")
        return tx_hash
    except Exception as e:
        print(f"Error sending transaction: {e}")
        return None

# Get nonce
def get_nonce():
    return web3.eth.get_transaction_count(WALLET_ADDRESS, "pending")

# Get current timestamp
def get_current_timestamp():
    return int(time.time())

# Load ABI
def load_abi(filepath):
    with open(filepath, 'r') as file:
        return json.load(file)
