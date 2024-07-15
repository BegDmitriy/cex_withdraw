from functions import *




def main():
    wallets = get_wallets()
    random.shuffle(wallets)

    for wallet in wallets:
        withdraw(exchange_name, wallet, withdraw_token_name, NameNetworks.arbitrum, amount)
        time.sleep(random.randint(300, 6000))



if __name__ == "__main__":
    main()
