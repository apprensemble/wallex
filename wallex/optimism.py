from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects

def convert_entry_from_decimals(entry):
  return int(entry['value']) * 10**-int(entry['token']['decimals'])

def parse_native_response_from_blockscout(rjson):
  entry = {
    'id': "ETH",
    'symbol': "ETH",
    'name': "Ethereum",
    'native_balance': 0.0,
    'blockchain': "optimism".capitalize(),
    'decimals': 18,
    'type': "EVM"
  }
  to_convert = { 'value':rjson['result'],'token':{'decimals':18}}
  entry['native_balance'] = convert_entry_from_decimals(to_convert)
  return entry

def get_tokens_balance_from_blockscout(account) -> dict:
  resultat = {}
  url_suffixe = "/addresses/"+account+"/token-balances"
  url = "https://optimism.blockscout.com/api/v2" + url_suffixe
  parameters = {
  }
  headers = {
    'Accepts': 'application/json'
  }
  rjson =  get_with_parameters(url,parameters,headers)
  if "message" in rjson:
    return resultat
  resultat = parse_response_from_blockscout(rjson)
  return resultat

def get_native_balance_from_blockscout(account) -> dict:

  entry ={ 'id': "ETH",
    'symbol': "ETH",
    'name': "Ethereum",
    'native_balance': 0.0,
    'blockchain': "optimism".capitalize(),
    'decimals': 18,
    'type': "EVM"
  }
  url = "https://optimism.blockscout.com/api"
  parameters = {
    'module':'account',
    'action': 'balance',
    'address': account
  }
  headers = {
    'Accepts': 'application/json'
  }
  rjson =  get_with_parameters(url,parameters,headers)
  if rjson['message'] == "OK":
    entry = parse_native_response_from_blockscout(rjson)
  return entry

def get_with_parameters(url,parameters,headers):

  session = Session()
  session.headers.update(headers)

  try:
    response = session.get(url, params=parameters)
  except (ConnectionError, Timeout, TooManyRedirects) as e:
    print(e)
  try:
    return response.json()
  except:
    return {}

def parse_response_from_blockscout(rjson):
  entries = {}
  for entry in rjson:
    if entry['token']['decimals'] and entry['token']['exchange_rate']:
      id = entry['token']['symbol']
      native_balance = convert_entry_from_decimals(entry)
      usd_balance = native_balance * float(entry['token']['exchange_rate'])
      entries[id] = {
        'id': id,
        'name': entry['token']['name'],
        'symbol': entry['token']['symbol'],
        'contract_address': entry['token']['address'],
        'native_balance': native_balance,
        'usd_balance': round(usd_balance,2),
        'blockchain': "optimism".capitalize(),
        'type': "EVM",
        'exchange_rate': float(entry['token']['exchange_rate'])
      }
      #print(entries[id]['symbol']," : ",entries[id]['usd_balance'])
    elif entry['token']['decimals']:
      continue     
      # je n'ajoute plus les elements sans exchange_rate car ce sont souvent des scams
      id = entry['token']['symbol']
      native_balance = convert_entry_from_decimals(entry)
      entries[id] = {
        'id': id,
        'name': entry['token']['name'],
        'symbol': entry['token']['symbol'],
        'contract_address': entry['token']['address'],
        'native_balance': native_balance,
        'blockchain': "Base",
        'type': "EVM",
      }
    else: continue
  return entries