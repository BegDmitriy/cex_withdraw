import os
import random

from dotenv import load_dotenv


load_dotenv()

def load_config():
    """
    Загрузка конфигурации API ключей и секретов из переменных окружения.

    Возвращает:
        dict: Словарь с конфигурацией, содержащий ключи и секреты для различных бирж:
            - 'okx_api_key' (str): API ключ для OKX.
            - 'okx_api_secret' (str): Секретный ключ для OKX.
            - 'okx_api_secret_phrase' (str): Парольная фраза для OKX.
            - 'bybit_api_key' (str): API ключ для Bybit.
            - 'bybit_api_secret' (str): Секретный ключ для Bybit.
            - 'binance_api_key' (str): API ключ для Binance.
            - 'binance_api_secret' (str): Секретный ключ для Binance.
    """
    # Загружаем конфигурацию из переменных окружения и сохраняем в словарь.
    config = {
        'okx_api_key': os.getenv('okx_api_key'),  # API ключ для OKX
        'okx_api_secret': os.getenv('okx_api_secret'),  # Секретный ключ для OKX
        'okx_api_secret_phrase': os.getenv('okx_api_secret_phrase'),  # Парольная фраза для OKX
        'bybit_api_key': os.getenv('bybit_api_key'),  # API ключ для Bybit
        'bybit_api_secret': os.getenv('bybit_api_secret'),  # Секретный ключ для Bybit
        'binance_api_key': os.getenv('binance_api_key'),  # API ключ для Binance
        'binance_api_secret': os.getenv('binance_api_secret')  # Секретный ключ для Binance
    }
    return config  # Возвращаем словарь конфигурации

# Указываем, что используется прокси (True)
is_proxy = True
# Задаем настройки прокси, загруженные из переменных окружения
proxies = {
    'http': os.getenv("proxy"),  # Прокси для HTTP
    'https': os.getenv('proxy')  # Прокси для HTTPS
}

class NameNetworks:
    erc20 = {
        "OKX": "ETH",
        "Binance": "ETH",
        "Bybit": "ERC20"
    }
    zksync = {
        "OKX": "zkSync Era",
        "Binance": "ZKSYNCERA",
        "Bybit": "ZKSYNC"
    }
    starknet = {
        "OKX": "Starknet",
        "Binance": "STARKNET",
        "Bybit": "STARKNET"
    }
    arbitrum = {
        "OKX": "Arbitrum One",
        "Binance": "ARBITRUM",
        "Bybit": "ARBI"
    }
    optimism = {
        "OKX": "Optimism",
        "Binance": "OPTIMISM",
        "Bybit": "OP"
    }
    bsc = {
        "OKX": "BSC",
        "Binance": "BSC",
        "Bybit": "BSC"
    }
    polygon = {
        "OKX": "Polygon",
        "Binance": "MATIC",
        "Bybit": "MATIC"
    }
    avalanche = {
        "OKX": "Avalanche C-Chain",
        "Binance": "AVAXC",
        "Bybit": "CAVAX"
    }
    fantom = {
        "OKX": "Fantom",
        "Binance": "FTM",
        "Bybit": "FTM"
    }
    linea = {
        "OKX": "Linea",
        "Binance": "LINEA",
        "Bybit": "LINEA"
    }
    base = {
        "OKX": "Base",
        "Binance": "BASE",
        "Bybit": "BASE"
    }

#  изменить для вывода с бирже ОКХ
withdraw_token_name = 'ETH'  # USDT, USDC

exchange_name = 'OKX'  # Bybit, Binance, OKX

amount_input = (20.3, 50.42)
amount = round(random.uniform(amount_input[0], amount_input[1]), 4)
