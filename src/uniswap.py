# uniswap.py
import json
from web3 import Web3
from config import (
    UNISWAP_QUOTER_ADDRESS,
    UNISWAP_ROUTER_ADDRESS,
    POOL_MANAGER_ADDRESS,
    TOKEN_A_ADDRESS,
    TOKEN_B_ADDRESS,
    UNISWAP_FEE,
    WALLET_ADDRESS
)
from utils import (
    web3,
    send_transaction,
    get_nonce,
    get_gas_price,
    get_current_timestamp
)

# ABI Loading with Error Handling
def load_abi_safe(file_path):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: ABI file not found: {file_path}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in ABI file: {file_path}")
        return None

# Load Uniswap ABIs
UNISWAP_QUOTER_ABI = load_abi_safe('abis/uniswap_quoter_abi.json')
UNISWAP_ROUTER_ABI = load_abi_safe('abis/uniswap_router_abi.json')
POOL_MANAGER_ABI = load_abi_safe('abis/uniswap_pool_manager_abi.json')
ERC20_ABI = load_abi_safe('abis/erc20_abi.json')

# Initialize Contracts Only If ABIs Are Loaded Successfully
if UNISWAP_QUOTER_ABI:
    uniswap_quoter = web3.eth.contract(address=UNISWAP_QUOTER_ADDRESS, abi=UNISWAP_QUOTER_ABI)
else:
    raise ValueError("Uniswap Quoter ABI could not be loaded.")

if UNISWAP_ROUTER_ABI:
    uniswap_router = web3.eth.contract(address=UNISWAP_ROUTER_ADDRESS, abi=UNISWAP_ROUTER_ABI)
else:
    raise ValueError("Uniswap Router ABI could not be loaded.")

if POOL_MANAGER_ABI:
    pool_manager = web3.eth.contract(address=POOL_MANAGER_ADDRESS, abi=POOL_MANAGER_ABI)
else:
    raise ValueError("Uniswap Pool Manager ABI could not be loaded.")

if ERC20_ABI:
    token_a = web3.eth.contract(address=TOKEN_A_ADDRESS, abi=ERC20_ABI)
    token_b = web3.eth.contract(address=TOKEN_B_ADDRESS, abi=ERC20_ABI)
else:
    raise ValueError("ERC20 ABI could not be loaded.")

def get_uniswap_price(amount_in):
    try:
        # PoolKeyの構造に従って適切なタプルを作成
        pool_key = (
            TOKEN_A_ADDRESS,  # currency0
            TOKEN_B_ADDRESS,  # currency1
            UNISWAP_FEE,      # fee
            60,               # tickSpacing（適切な値を設定）
            "0x0000000000000000000000000000000000000000"  # hooks (なしの場合 0x0)
        )

        params = (
            pool_key,   # プールのキー
            True,       # zeroForOne（TOKEN_A から TOKEN_B への変換なら True）
            amount_in,  # 交換するトークンの量
            b''         # hookData（特になし）
        )

        # コントラクト関数を呼び出す
        result = uniswap_quoter.functions.quoteExactInputSingle(params).call()

        if isinstance(result, tuple) and len(result) == 2:
            amount_out, gas_estimate = result
        else:
            print(f"Unexpected Uniswap response: {result}")
            return None, None

        return amount_out, gas_estimate

    except Exception as e:
        print(f"Error fetching Uniswap v4 price: {e}")
        return None, None





def swap_on_uniswap(amount_in, amount_out_min):
    try:
        deadline = get_current_timestamp() + 60  # Transaction deadline set to 60 seconds from now
        
        pool_key = (
            TOKEN_A_ADDRESS,
            TOKEN_B_ADDRESS,
            UNISWAP_FEE
        )
        
        # Prepare the exactInputSingle parameters as per Uniswap v4's Router
        swap_params = {
            "poolKey": pool_key,
            "recipient": WALLET_ADDRESS,
            "amountIn": amount_in,
            "amountOutMinimum": amount_out_min,
            "hookData": b''  # Adjust if hooks are used
        }
        
        # Build the transaction
        txn = uniswap_router.functions.exactInputSingle(swap_params).build_transaction({
            "from": WALLET_ADDRESS,
            "gas": 300000,  # Adjust gas limit as necessary
            "gasPrice": int(get_gas_price() * 1.5),  # Increase gas price by 1.5x for priority
            "nonce": get_nonce(),
            "deadline": deadline
        })
        
        # Send the transaction using the utility function
        tx_hash = send_transaction(txn)
        return tx_hash
    except Exception as e:
        print(f"Error executing Uniswap v4 swap: {e}")
        return None

def approve_uniswap(amount):
    try:
        # Build the approval transaction
        txn = token_a.functions.approve(
            UNISWAP_ROUTER_ADDRESS,
            amount
        ).build_transaction({
            "from": WALLET_ADDRESS,
            "gas": 100000,  # Adjust gas limit as necessary
            "gasPrice": int(get_gas_price() * 1.5),  # Increase gas price by 1.5x for priority
            "nonce": get_nonce(),
        })
        
        # Send the transaction
        tx_hash = send_transaction(txn)
        
        if tx_hash:
            print(f"Uniswap v4 approval transaction sent: {Web3.to_hex(tx_hash)}")
        else:
            print("Uniswap v4 approval transaction failed.")
        
        return tx_hash
    except Exception as e:
        print(f"Error approving Uniswap v4 router: {e}")
        return None
