# config.py
from web3 import Web3
import os

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

RPC_URL = os.getenv("RPC_URL")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
WALLET_ADDRESS = Web3.to_checksum_address(os.getenv("WALLET_ADDRESS"))

# Uniswap Configuration
UNISWAP_FEE = 3000
UNISWAP_QUOTER_ADDRESS = Web3.to_checksum_address("0x61b3f2011a92d183c7dbadbda940a7555ccf9227")
UNISWAP_ROUTER_ADDRESS = Web3.to_checksum_address("0x3a9d48ab9751398bbfa63ad67599bb04e4bdf98b")
POOL_MANAGER_ADDRESS = Web3.to_checksum_address("0xE03A1074c86CFeDd5C142C4F04F1a1536e203543")

# Balancer Configuration
BALANCER_VAULT_ADDRESS = Web3.to_checksum_address("0xBA12222222228d8Ba445958a75a0704d566BF2C8")
BALANCER_POOL_ID = "0x001065df0f45f02ff0d581e875915648b0b7ca1f000200000000000000000098"


# Token Addresses (DAI/WETH) - Checksum addresses
TOKEN_A_ADDRESS = Web3.to_checksum_address("0x68194a729c2450ad26072b3d33adacbcef39d574")  # DAI
TOKEN_B_ADDRESS = Web3.to_checksum_address("0xda9d4f9b69ac6c22e444ed9af0cfc043b7a7f53f")  # USDC
