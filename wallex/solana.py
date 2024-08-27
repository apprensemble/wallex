from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects

def get_with_parameters(url,parameters,headers):

  session = Session()
  session.headers.update(headers)

  try:
    response = session.get(url, params=parameters)
  except (ConnectionError, Timeout, TooManyRedirects) as e:
    print(e)
  return response.json()

def get_spl_tokens_balance_from_moralis(api_key,account):
    url_suffixe = account+"/tokens"
    url = 'https://solana-gateway.moralis.io/account/mainnet/' + url_suffixe
    parameters = {
    }
    headers = {
        'Accepts': 'application/json',
        'X-API-Key': api_key

    }
    rjson =  get_with_parameters(url,parameters,headers)
    entries = {}

    for element in rjson:
        doublons = False
        if element['symbol'].upper() in entries.keys():
            doublons = True
        else:
            doublons = False
        symbol = element['symbol'].upper()
        entries[symbol] = {
            'id': symbol,
            'symbol': symbol,
            'name': element['name'],
            'native_balance': element['amount'],
            'blockchain': "Solana",
            'type': "SVM",
            'doublons': doublons,
            'contract_address': element['associatedTokenAddress']
        }
        if doublons:
            entries[symbol]['doublons'] = True
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

    url_suffixe = account+'/balance'
    url = 'https://solana-gateway.moralis.io/account/mainnet/' + url_suffixe
    parameters = {
    }
    headers = {
        'Accepts': 'application/json',
        'X-API-Key': api_key
    }
    rjson =  get_with_parameters(url,parameters,headers)
    entry["native_balance"] = float(rjson['solana'])
    return entry

