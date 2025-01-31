import time
import logging
from web3 import Web3
from uniswap import (
    get_uniswap_price,
    swap_on_uniswap,
    approve_uniswap
)
from balancer import (  # Updated from curve to balancer
    get_balancer_price,
    swap_on_balancer,
    approve_balancer
)

# ログ設定
logging.basicConfig(
    filename="bot_log.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# アービトラージの利幅設定（例: 1%）
ARBITRAGE_THRESHOLD = 0.01

# スワップ量の設定（例: 10 DAI）
AMOUNT_IN = Web3.to_wei(10, 'ether')  # 10 DAI assuming 18 decimals

def main():
    logging.info("Bot started.")
    
    # Approve Uniswap Router
    print("Approving Uniswap Router...")
    logging.info("Approving Uniswap Router...")
    approve_tx = approve_uniswap(Web3.to_wei(1000, 'ether'))
    if approve_tx:
        print(f"Approval TX Hash: {Web3.to_hex(approve_tx)}")
        logging.info(f"Uniswap Approval TX Hash: {Web3.to_hex(approve_tx)}")
    else:
        print("Approval transaction failed.")
        logging.error("Uniswap approval transaction failed.")

    # Approve Balancer Pool
    print("Approving Balancer Pool...")
    logging.info("Approving Balancer Pool...")
    approve_balancer_tx = approve_balancer(Web3.to_wei(1000, 'ether'))
    if approve_balancer_tx:
        print(f"Balancer Approval TX Hash: {Web3.to_hex(approve_balancer_tx)}")
        logging.info(f"Balancer Approval TX Hash: {Web3.to_hex(approve_balancer_tx)}")
    else:
        print("Balancer approval transaction failed. Check gas price and nonce.")  
        logging.error("Balancer approval transaction failed. Check gas price and nonce.")

    # Bot main loop
    while True:
        try:
            logging.info("Fetching Uniswap and Balancer prices...")
            # Fetch prices
            uniswap_price, uniswap_gas = get_uniswap_price(AMOUNT_IN)
            balancer_price = get_balancer_price(AMOUNT_IN)

            if uniswap_price is None or balancer_price is None:
                print("Failed to fetch price data.")
                logging.error(f"Failed to fetch price data. Uniswap: {uniswap_price}, Balancer: {balancer_price}")
                time.sleep(10)
                continue

            uniswap_price_eth = Web3.from_wei(uniswap_price, 'ether')
            balancer_price_eth = Web3.from_wei(balancer_price, 'ether')

            print(f"Uniswap Price: {uniswap_price_eth} WETH")
            print(f"Balancer Price: {balancer_price_eth} WETH")
            logging.info(f"Uniswap Price: {uniswap_price_eth} WETH, Balancer Price: {balancer_price_eth} WETH")

            # Detect arbitrage opportunity
            if uniswap_price > balancer_price * (1 + ARBITRAGE_THRESHOLD):
                print("Arbitrage opportunity detected: Sell on Uniswap, Buy on Balancer")
                logging.info("Arbitrage opportunity detected: Sell on Uniswap, Buy on Balancer")

                # Sell on Uniswap (DAI -> WETH)
                amount_out_min_uniswap = int(balancer_price * (1 - ARBITRAGE_THRESHOLD))
                tx1 = swap_on_uniswap(AMOUNT_IN, amount_out_min_uniswap)
                if tx1:
                    print(f"Uniswap Swap TX: {Web3.to_hex(tx1)}")
                    logging.info(f"Uniswap Swap TX: {Web3.to_hex(tx1)}")
                else:
                    print("Uniswap swap transaction failed.")
                    logging.error("Uniswap swap transaction failed.")

                # Buy on Balancer (WETH -> DAI)
                amount_out_min_balancer = int(balancer_price * (1 - ARBITRAGE_THRESHOLD))
                tx2 = swap_on_balancer(amount_out_min_balancer, AMOUNT_IN)
                if tx2:
                    print(f"Balancer Swap TX: {Web3.to_hex(tx2)}")
                    logging.info(f"Balancer Swap TX: {Web3.to_hex(tx2)}")
                else:
                    print("Balancer swap transaction failed.")
                    logging.error("Balancer swap transaction failed.")

            elif balancer_price > uniswap_price * (1 + ARBITRAGE_THRESHOLD):
                print("Arbitrage opportunity detected: Sell on Balancer, Buy on Uniswap")
                logging.info("Arbitrage opportunity detected: Sell on Balancer, Buy on Uniswap")

                # Sell on Balancer (DAI -> WETH)
                amount_out_min_balancer = int(uniswap_price * (1 - ARBITRAGE_THRESHOLD))
                tx1 = swap_on_balancer(AMOUNT_IN, amount_out_min_balancer)
                if tx1:
                    print(f"Balancer Swap TX: {Web3.to_hex(tx1)}")
                    logging.info(f"Balancer Swap TX: {Web3.to_hex(tx1)}")
                else:
                    print("Balancer swap transaction failed.")
                    logging.error("Balancer swap transaction failed.")

                # Buy on Uniswap (WETH -> DAI)
                amount_out_min_uniswap = AMOUNT_IN  # Set the obtained price as minimum output
                tx2 = swap_on_uniswap(amount_out_min_uniswap, AMOUNT_IN)
                if tx2:
                    print(f"Uniswap Swap TX: {Web3.to_hex(tx2)}")
                    logging.info(f"Uniswap Swap TX: {Web3.to_hex(tx2)}")
                else:
                    print("Uniswap swap transaction failed.")
                    logging.error("Uniswap swap transaction failed.")

            else:
                print("No arbitrage opportunity detected.")
                logging.info("No arbitrage opportunity detected.")

        except Exception as e:
            print(f"An error occurred: {e}")
            logging.error(f"An error occurred: {e}", exc_info=True)

        # Wait for a while before the next check
        time.sleep(10)

if __name__ == "__main__":
    main()