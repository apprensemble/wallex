from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from moralis import sol_api


def get_spl_tokens_balance_from_moralis(api_key,account):
    entries = {}
    params = {
    "network": "mainnet",
    "address": account
    }

    result = sol_api.account.get_spl(
    api_key=api_key,
    params=params,
    )

    for element in result:
        doublons = False
        if element['symbol'] in entries.keys():
            doublons = True
        id = element['symbol']
        entries[element['symbol']] = {
            'id': id,
            'symbol': element['symbol'],
            'name': element['name'],
            'native_balance': element['amount'],
            'blockchain': "Solana",
            'type': "SVM",
            'contract_address': element['associatedTokenAddress']
        }
        if doublons:
            entries[element['symbol']]['doublons'] = True
    return entries   

def get_sol_balance_from_moralis(api_key,account):
    entry = {
        'id': "SOL",
        'symbol': "SOL",
        'name': "Solana",
        'native_balance': 0.0,
        'blockchain': "Solana",
        'type': "SVM"
    }
    params = {
    "network": "mainnet",
    "address": account
    }

    result = sol_api.account.balance(
    api_key=api_key,
    params=params,
    )
    entry["native_balance"] = float(result['solana'])
    return entry

