import random
import time
from config import *
import ccxt
from pprint import pprint
import requests



def get_wallets(path: str = "wallets.txt") -> list[str]:
    """
    Get wallets from the file with the path in the parameter
    :return: list of wallets
    """
    with open(path, "r") as file:  # Открываем файл на чтение
        wallets = file.read().split("\n")  # Читаем файл и разбиваем его по строкам
    return wallets  # Возвращаем список кошельков

def ceh_connecnt(ceh_name: str):
    exchange = None
    config = load_config()

    if ceh_name == 'OKX':
        exchange = ccxt.okx({
            'apiKey': config['okx_api_key'],
            'secret': config['okx_api_secret'],
            'password': config['okx_api_secret_phrase'],
        })

    elif ceh_name == 'Binance':
        exchange = ccxt.binance({
            'apiKey': config['binance_api_key'],
            'secret': config['binance_api_secret'],
        })

    elif ceh_name == 'Bybit':
        exchange = ccxt.bybit({
            'apiKey': config['bybit_api_key'],
            'secret': config['bybit_api_secret'],
        })

    else:
        print('Неизвестная биржа')

    if exchange and is_proxy:
        exchange.proxies = proxies

    return exchange


def get_okx_fee(token_name: str, network_name: str) -> float:
    exchange = ceh_connecnt('OKX')
    chain = f'{token_name}-{network_name}'
    try:
        exchange.load_markets()
    except ccxt.BaseError as e:
        print(f"Ошибка при загрузке рынков: {e}")
        return 0.0

    try:
        currencies = exchange.currencies
        token_data = currencies.get(token_name, {})
    except KeyError as e:
        print(f"Ошибка при доступе к данным о валюте: {e}")
        return 0.0

    if not token_data:
        print(f"Токен {token_name} не найден на бирже OKX.")
        return 0.0

    try:
        token_networks = token_data["networks"]
    except KeyError as e:
        print(f"Ошибка при доступе к данным о сетях токена: {e}")
        return 0.0

    for network_data in token_networks.values():
        if chain == network_data['id']:
            try:
                return float(network_data['fee'])
            except KeyError as e:
                print(f"Ошибка при доступе к комиссии на вывод: {e}")
                return 0.0
            except ValueError as e:
                print(f"Ошибка преобразования комиссии на вывод в число: {e}")
                return 0.0

    print(f"Сеть {network_name} для токена {token_name} не найдена на бирже OKX.")
    return 0.0

def get_binance_fee(token_name: str, network_name: str) -> float:
    exchange = ceh_connecnt('Binance')
    try:
        exchange.load_markets()
    except ccxt.BaseError as e:
        print(f"Ошибка при загрузке рынков: {e}")
        return 0.0

    try:
        currencies = exchange.currencies
        token_data = currencies.get(token_name, {})
    except KeyError as e:
        print(f"Ошибка при доступе к данным о валюте: {e}")
        return 0.0

    if not token_data:
        print(f"Токен {token_name} не найден на бирже Binance.")
        return 0.0

    try:
        token_networks = token_data["info"]['networkList']
    except KeyError as e:
        print(f"Ошибка при доступе к данным о сетях токена: {e}")
        return 0.0

    for network_data in token_networks:
        if network_data['network'] == network_name:
            try:
                return float(network_data['withdrawFee'])
            except KeyError as e:
                print(f"Ошибка при доступе к комиссии на вывод: {e}")
                return 0.0
            except ValueError as e:
                print(f"Ошибка преобразования комиссии на вывод в число: {e}")
                return 0.0

    print(f"Сеть {network_name} для токена {token_name} не найдена на бирже Binance.")
    return 0.0


def get_bybit_fee(token_name: str, network_name: str) -> float:
    exchange = ceh_connecnt('Bybit')

    """
    Получение комиссии на вывод токена с биржи Bybit для указанной сети.

    Параметры:
    exchange (ccxt.okx): Экземпляр биржи OKX (должен быть заменен на ccxt.bybit для Bybit).
    token_name (str): Имя токена для вывода (например, 'USDT').
    network_name (str): Имя сети для вывода (например, 'ERC20').

    Возвращает:
    float: Комиссия на вывод токена. Если возникают ошибки, возвращает 0.0.
    """

    # Формируем идентификатор цепочки для поиска
    chain = f'{token_name}-{network_name}'

    # Загружаем информацию о рынках и валютах
    try:
        exchange.load_markets()
    except ccxt.BaseError as e:
        print(f"Ошибка при загрузке рынков: {e}")
        return 0.0

    # Получаем данные о токенах
    try:
        currencies = exchange.currencies
        token_data = currencies.get(token_name, {})
    except KeyError as e:
        print(f"Ошибка при доступе к данным о валюте: {e}")
        return 0.0

    # Проверяем, существуют ли данные о токене
    if not token_data:
        print(f"Токен {token_name} не найден на бирже Bybit.")
        return 0.0

    # Получаем информацию о сетях для токена
    try:
        token_networks = token_data["info"]['chains']
    except KeyError as e:
        print(f"Ошибка при доступе к данным о сетях токена: {e}")
        return 0.0

    # Ищем нужную сеть и получаем комиссию на вывод
    for network_data in token_networks:
        if network_data['chain'] == network_name:
            try:
                return float(network_data['withdrawFee'])
            except KeyError as e:
                print(f"Ошибка при доступе к комиссии на вывод: {e}")
                return 0.0
            except ValueError as e:
                print(f"Ошибка преобразования комиссии на вывод в число: {e}")
                return 0.0

    # Если нужная сеть не найдена
    print(f"Сеть {network_name} для токена {token_name} не найдена на бирже Bybit.")
    return 0.0


def bybit_withdraw(address: str, token_name: str, network_name: str, amount: float, tag=None) -> dict:
    """
    Функция для вывода токенов с биржи Bybit.

    Параметры:
    exchange (ccxt.bybit): Экземпляр биржи Bybit.
    address (str): Адрес, на который нужно вывести токены.
    token_name (str): Имя токена для вывода (например, 'USDT').
    network_name (str): Имя сети для вывода (например, 'ERC20').
    amount (float): Количество токенов для вывода.
    tag (str, optional): Дополнительный тег (например, для сетей XRP, XLM, EOS и т.д.).

    Возвращает:
    dict: Результат операции вывода.
    """

    # Загрузка конфигурации и создание экземпляра биржи с ключами API
    config = load_config()
    global BYBIT_TIMESTAMP
    # Создание подключение к бирже Bybit с ключами API
    exchange = ceh_connecnt('Bybit')
    # Загрузка информации о рынках и валютах
    exchange.load_markets()

    # Получение комиссии на вывод токена
    fee = get_bybit_fee(token_name, network_name)
    amount -= fee  # Уменьшаем сумму вывода на комиссию
    amount = round(amount, 8)  # Округляем сумму до 8 знаков после запятой
    print(f'Комиссия составляет: {fee}')

    # Получение текущего времени с сервера Bybit
    BYBIT_TIMESTAMP = exchange.fetch_time()

    try:
        # Параметры для вывода
        params = {
            "timestamp": BYBIT_TIMESTAMP,
            'chain': network_name,
            'forceChain': 1,  # 0 для внутреннего перевода, 1 для вывода на блокчейн
            'accountType': "SPOT",  # "SPOT" или "FUND" в зависимости от вашего аккаунта
            'feeType': 1,  # 0 для ручного расчета комиссии, 1 для автоматического вычета
        }

        # Добавление тега, если он указан
        if tag:
            params['tag'] = tag

        # Информация для пользователя перед выполнением операции
        print(f"Начинаем вывод токена {token_name} с биржи Bybit в сети {network_name} на сумму {amount}")
        print('Ваш IP:')

        # Проверка текущего IP-адреса через внешний API
        try:
            ip = requests.get("https://api.ipify.org/").text
            print(ip)
        except Exception as e:
            print(f"Не удалось получить IP-адрес: {e}")

        # Выполнение операции вывода
        bybit_tx = exchange.withdraw(token_name, amount, address, params=params)
        return bybit_tx

    except ccxt.BaseError as e:
        # Обработка ошибок, связанных с API биржи
        print(f"Ошибка API биржи: {type(e).__name__}, {str(e)}")
    except KeyError as e:
        # Обработка ошибок, связанных с неправильными параметрами
        print(f"Ошибка параметров: {type(e).__name__}, {str(e)}")
    except ValueError as e:
        # Обработка ошибок преобразования данных
        print(f"Ошибка данных: {type(e).__name__}, {str(e)}")
    except Exception as e:
        # Общая обработка всех прочих ошибок
        print(f"Неизвестная ошибка: {type(e).__name__}, {str(e)}")

    return {}

def okx_withdraw(address: str, token_name: str, network_name: str, amount: float) -> dict:
    """
    Функция для вывода токенов с биржи OKX.

    Параметры:
    exchange (ccxt.okx): Экземпляр биржи OKX.
    address (str): Адрес, на который нужно вывести токены.
    token_name (str): Имя токена для вывода (например, 'USDT').
    network_name (str): Имя сети для вывода (например, 'ERC20').
    amount (float): Количество токенов для вывода.

    Возвращает:
    None
    """

    # Загрузка конфигурации и создание экземпляра биржи с ключами API
    config = load_config()
    exchange = ceh_connecnt('OKX')

    # Получение комиссии на вывод токена
    fee = get_okx_fee(token_name, network_name)
    print(f'Комиссия составляет: {fee}')

    try:
        # Параметры для вывода
        params = {
            'ccy': token_name,
            'toAddr': address,
            'amt': amount,
            'fee': fee,
            'dest': "4",  # Убедитесь, что это значение корректно для вашей сети
            'chain': f'{token_name}-{network_name}'
        }

        # Информация для пользователя перед выполнением операции
        print(f"Начинаем вывод токена {token_name} с биржи OKX в сети {network_name} на сумму {amount}")
        print('Ваш IP:')

        # Проверка текущего IP-адреса через внешний API
        try:
            ip = exchange.fetch("https://api.ipify.org/")
            print(ip)
        except Exception as e:
            print(f"Не удалось получить IP-адрес: {e}")

        # Выполнение операции вывода
        tx = exchange.withdraw(token_name, amount, address, params=params)
        pprint(tx)

    except ccxt.BaseError as e:
        # Обработка ошибок, связанных с API биржи
        print(f"Ошибка API биржи: {type(e).__name__}, {str(e)}")
    except KeyError as e:
        # Обработка ошибок, связанных с неправильными параметрами
        print(f"Ошибка параметров: {type(e).__name__}, {str(e)}")
    except ValueError as e:
        # Обработка ошибок преобразования данных
        print(f"Ошибка данных: {type(e).__name__}, {str(e)}")
    except Exception as e:
        # Общая обработка всех прочих ошибок
        print(f"Неизвестная ошибка: {type(e).__name__}, {str(e)}")

    return {}

def binance_withdraw(address: str, token_name: str, network_name: str, amount: float) -> dict:
    """
       Функция для вывода токенов с биржи Binance.

       Параметры:
       address (str): Адрес, на который нужно вывести токены.
       token_name (str): Имя токена для вывода (например, 'USDT').
       network_name (str): Имя сети для вывода (например, 'BSC').
       amount (float): Количество токенов для вывода.

       Возвращает:
       dict: Информация о транзакции вывода.
       """

    # Загрузка конфигурации и создание экземпляра биржи с ключами API
    config = load_config()

    exchange = ceh_connecnt('Binance')
    if exchange is None:
        print("Не удалось создать экземпляр биржи Binance.")
        return {}

    # Получение комиссии на вывод токена
    fee = get_binance_fee(token_name, network_name)
    print(f'Комиссия составляет: {fee}')
    amount -= fee  # Уменьшаем сумму вывода на комиссию

    try:
        # Параметры для вывода
        params = {
            'network': network_name,
        }

        # Информация для пользователя перед выполнением операции
        print(f"Начинаем вывод токена {token_name} с биржи Binance в сети {network_name} на сумму {amount}")
        print('Ваш IP:')

        # Проверка текущего IP-адреса через внешний API
        try:
            ip = exchange.fetch("https://api.ipify.org/")
            print(ip)
        except Exception as e:
            print(f"Не удалось получить IP-адрес: {e}")

        # Выполнение операции вывода
        binance_tx = exchange.withdraw(token_name, amount, address, params=params)
        pprint(binance_tx)

        return binance_tx

    except ccxt.BaseError as e:
        # Обработка ошибок, связанных с API биржи
        print(f"Ошибка API биржи: {type(e).__name__}, {str(e)}")
    except KeyError as e:
        # Обработка ошибок, связанных с неправильными параметрами
        print(f"Ошибка параметров: {type(e).__name__}, {str(e)}")
    except ValueError as e:
        # Обработка ошибок преобразования данных
        print(f"Ошибка данных: {type(e).__name__}, {str(e)}")
    except Exception as e:
        # Общая обработка всех прочих ошибок
        print(f"Неизвестная ошибка: {type(e).__name__}, {str(e)}")

    return {}

def withdraw(
        ceh_name: str,
        address: str,
        token_name: str,
        network: dict,
        amount: float
) -> bool:
    """
    Функция для выполнения вывода токенов с различных бирж.

    Параметры:
    ceh_name (str): Имя биржи (OKX, Binance или Bybit).
    address (str): Адрес, на который нужно вывести токены.
    token_name (str): Имя токена для вывода (например, 'USDT').
    network (dict): Словарь, содержащий имена сетей для каждой биржи.
    amount (float): Количество токенов для вывода.

    Возвращает:
    bool: True, если вывод прошел успешно, False в противном случае.
    """
    exchange = ceh_connecnt(ceh_name)
    if exchange is None:
        return False

    print(exchange.id)
    # Получаем имя сети для данной биржи
    network_name = network.get(ceh_name)
    if not network_name:
        print(f"Сеть для биржи {exchange.id} не найдена.")
        return False

    print(f'Network name for {exchange.id}: {network_name}')

    # Выполняем вывод в зависимости от биржи
    try:
        if exchange.id.lower() == 'okx':
            tx = okx_withdraw(address, token_name, network_name, amount)
        elif exchange.id.lower() == 'binance':
            tx = binance_withdraw(address, token_name, network_name, amount)
        elif exchange.id.lower() == 'bybit':
            tx = bybit_withdraw(address, token_name, network_name, amount)
        else:
            print('Неизвестная биржа')
            return False

        # Получаем ID транзакции вывода
        id_tx = tx.get('id')
        if not id_tx:
            print('Не удалось получить ID транзакции.')
            return False

        # Проверяем статус транзакции в течение определенного времени
        if ceh_name.lower() == 'okx' or ceh_name.lower() == 'binance':
            for _ in range(20):
                tx_status = exchange.fetch_withdrawal(id_tx)
                if tx_status.get('status') != 'pending':
                    if tx_status.get('status') == 'ok':
                        print(f'Вывод с биржи {exchange.id} токена {token_name} в сети {network_name} на сумму {amount} на адрес {address}, прошел успешно')
                        return True
                    else:
                        break
                time.sleep(random.randint(30, 60))
        elif ceh_name.lower() == 'bybit':
            BYBIT_TIMESTAMP = exchange.fetch_time()
            for attempt in range(15):  # Попытаться проверить статус до 15 раз
                try:
                    tx_list = exchange.fetch_withdrawals(code=token_name, since=BYBIT_TIMESTAMP, params={"withdrawId": id_tx})
                    print(f"Attempt {attempt + 1}: tx status {tx_list}")

                    for transaction in tx_list:
                        if transaction['id'] == id_tx:
                            status = transaction['info']['status']
                            if status == 'success' or status == 'BlockchainConfirmed':
                                print(f"Вывод {exchange.id} {amount} {token_name} на адрес {address} в сеть {network_name} прошел успешно")
                                return True
                            if status in ['Pending', 'SecurityCheck']:
                                print(f"Transaction {id_tx} is still pending. Checking again...")
                                sleep_time = random.randint(30, 60)
                                print(f"Waiting for {sleep_time} seconds before checking again.")
                                time.sleep(sleep_time)
                            else:
                                print(f"Transaction {id_tx} failed. Status: {status}")
                                return False
                except Exception as e:
                    print(f'ОШИБКА!!! Вывод с биржи {exchange.id} токена {token_name} в сети {network_name} на сумму {amount} на адрес {address}, не прошел, транзакция {id_tx}. Ошибка: {e}')
                    return False

            print(f'ОШИБКА!!! Вывод с биржи {exchange.id} токена {token_name} в сети {network_name} на сумму {amount} на адрес {address}, не прошел, транзакция {id_tx}')
            return False

        # Сообщение об ошибке, если вывод не прошел успешно
        print(f'ОШИБКА!!! Вывод с биржи {exchange.id} токена {token_name} в сети {network_name} на сумму {amount} на адрес {address}, не прошел')
        return False
    except Exception as e:
        print(f"Произошла ошибка при выполнении вывода: {str(e)}")
        return False


# def get_okx_balances(exchange):
#     exchange.load_markets()
#     funding_balance = exchange.fetch_balance({'type': 'funding'})
#     spot_balance = exchange.fetch_balance({'type': 'spot'})
#     return {
#         'funding': funding_balance,
#         'spot': spot_balance
#     }
#
# def get_binance_balances(exchange):
#     exchange.load_markets()
#     funding_balance = exchange.fetch_balance({'type': 'funding'})
#     spot_balance = exchange.fetch_balance({'type': 'spot'})
#     return {
#         'funding': funding_balance,
#         'spot': spot_balance
#     }
#
# def get_bybit_balances(exchange):
#     exchange.load_markets()
#     funding_balance = exchange.fetch_balance({'type': 'funding'})
#     spot_balance = exchange.fetch_balance({'type': 'spot'})
#     return {
#         'funding': funding_balance,
#         'spot': spot_balance
#     }
#
# def get_balances(exchange):
#     balances = {}
#
#     if exchange.id == 'okx':
#         balances = get_okx_balances(exchange)
#     elif exchange.id == 'binance':
#         balances = get_binance_balances(exchange)
#     elif exchange.id == 'bybit':
#         balances = get_bybit_balances(exchange)
#     else:
#         raise ValueError('Неизвестное подключение')
#
#     return balances






# def get_okx_tokens():
#     """
#     Возвращает список всех торговых пар биржи OKX.
#     Функция создает экземпляр биржи OKX с использованием библиотеки ccxt,
#     загружает информацию о всех доступных рынках и извлекает список торговых пар.
#     Returns:
#         list: Список строк, где каждая строка представляет собой торговую пару.
#     """
#
#     # Создаем экземпляр биржи OKX
#     okx_exchange = ccxt.okx()
#
#     # Загружаем информацию о рынках
#     okx_markets = okx_exchange.load_markets()
#
#     # Извлекаем список торговых пар
#     okx_trading_pairs = list(okx_markets.keys())
#
#     return okx_trading_pairs
#
# def get_binance_tokens():
#     """
#         Возвращает список всех торговых пар биржи Binance.
#         Функция создает экземпляр биржи Binance с использованием библиотеки ccxt,
#         загружает информацию о всех доступных рынках и извлекает список торговых пар.
#         Returns:
#             list: Список строк, где каждая строка представляет собой торговую пару.
#         """
#
#     # Создаем экземпляр биржи Binance
#     binance_exchange = ccxt.binance()
#     # Загружаем информацию о рынках
#     binance_markets = binance_exchange.load_markets()
#     # Извлекаем список торговых пар
#     binance_traiding_pairs = list(binance_markets.keys())
#     return binance_traiding_pairs

if __name__ == "__main__":
    pass
