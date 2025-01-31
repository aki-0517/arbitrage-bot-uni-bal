# balancer.py
import json
from web3 import Web3
from config import (
    BALANCER_POOL_ID,
    BALANCER_VAULT_ADDRESS,
    TOKEN_A_ADDRESS,
    TOKEN_B_ADDRESS,
    WALLET_ADDRESS
)
from uniswap import ERC20_ABI
from utils import web3, send_transaction, get_nonce, get_gas_price, get_current_timestamp

# Load ABI with error handling
def load_abi_safe(file_path):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: ABI file not found: {file_path}")
        return None

BALANCER_VAULT_ABI = load_abi_safe('abis/balancer_vault_abi.json')

# Setup contracts
if BALANCER_VAULT_ABI:
    balancer_vault = web3.eth.contract(address=BALANCER_VAULT_ADDRESS, abi=BALANCER_VAULT_ABI)
else:
    raise ValueError("Balancer Vault ABI is not loaded correctly.")

if ERC20_ABI:
    token_a = web3.eth.contract(address=TOKEN_A_ADDRESS, abi=ERC20_ABI)
    token_b = web3.eth.contract(address=TOKEN_B_ADDRESS, abi=ERC20_ABI)
else:
    raise ValueError("ERC20 ABI is not loaded correctly.")

def get_balancer_price(amount_in):
    try:
        # プールのトークン残高を取得
        tokens, balances, lastChangeBlock = balancer_vault.functions.getPoolTokens(BALANCER_POOL_ID).call()

        # amount_in がプールの最大流動性を超えていないかチェック
        max_liquidity = min(int(balances[0]), int(balances[1]))  # 2つのトークンのうち少ない方を選ぶ
        if amount_in > max_liquidity:
            print(f"Amount in ({amount_in}) exceeds max liquidity ({max_liquidity})")
            return None

        swap_kind = 0  # 0: GivenIn, 1: GivenOut
        assets = [TOKEN_A_ADDRESS, TOKEN_B_ADDRESS]

        swaps = [{
            "poolId": BALANCER_POOL_ID,
            "assetInIndex": 0,
            "assetOutIndex": 1,
            "amount": amount_in,
            "userData": b''  # ユーザーデータの指定（通常は空）
        }]

        funds = {
            "sender": WALLET_ADDRESS,
            "recipient": WALLET_ADDRESS,
            "fromInternalBalance": False,
            "toInternalBalance": False
        }

        result = balancer_vault.functions.queryBatchSwap(
            swap_kind, swaps, assets, funds
        ).call()

        if isinstance(result, list) and len(result) > 1:
            amount_out = int(result[1])  # `result` のリストから値を取得
        else:
            print(f"Unexpected Balancer response: {result}")
            return None

        return amount_out / 1e18  # Wei → ETH
    except Exception as e:
        print(f"Error fetching Balancer price: {e}")
        return None


def swap_on_balancer(amount_in, amount_out_min):
    """
    Execute a swap on Balancer Vault.
    :param amount_in: Amount of input token (Wei)
    :param amount_out_min: Minimum amount of output token (Wei)
    :return: Transaction hash
    """
    try:
        deadline = get_current_timestamp() + 60  # 60 seconds from now

        # Balancer V2 uses the Vault's swap function with a complex set of parameters
        # You'll need to construct the appropriate swap request
        # Here's a simplified example:

        swap_request = {
            'sender': WALLET_ADDRESS,
            'recipient': WALLET_ADDRESS,
            'assets': [TOKEN_A_ADDRESS, TOKEN_B_ADDRESS],
            'minAmounts': [0, amount_out_min],
            'userData': b'',  # Encoded user data for the swap
            'toInternalBalance': False
        }

        txn = balancer_vault.functions.swap(
            swap_request
        ).build_transaction({
            "from": WALLET_ADDRESS,
            "gas": 500000,  # Adjust gas limit as needed
            "gasPrice": int(get_gas_price()),
            "nonce": get_nonce(),
        })

        tx_hash = send_transaction(txn)
        return tx_hash
    except Exception as e:
        print(f"Error executing Balancer swap: {e}")
        return None

def approve_balancer(amount):
    """
    Approve Balancer Vault to spend the input token.
    :param amount: Amount to approve (Wei)
    :return: Transaction hash
    """
    try:
        txn = token_a.functions.approve(
            BALANCER_VAULT_ADDRESS,
            amount
        ).build_transaction({
            "from": WALLET_ADDRESS,
            "gas": 100000,
            "gasPrice": int(get_gas_price() * 1.2),  # Increase gas price by 1.5x
            "nonce": get_nonce(),
        })

        tx_hash = send_transaction(txn)
        if tx_hash:
            print(f"Balancer Vault approval transaction sent: {Web3.to_hex(tx_hash)}")
        else:
            print("Balancer Vault approval transaction failed.")
        return tx_hash
    except Exception as e:
        print(f"Error approving Balancer Vault: {e}")
        return None
