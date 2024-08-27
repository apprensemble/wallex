from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects

def get_tokens_balance_from_blockscout(account) -> dict:
  url_suffixe = "/addresses/"+account+"/token-balances"
  url = "https://arbitrum.blockscout.com/api/v2" + url_suffixe
  parameters = {
  }
  headers = {
    'Accepts': 'application/json'
  }
  rjson =  get_with_parameters(url,parameters,headers)
  return parse_response_from_blockscout(rjson)

def get_native_balance_from_blockscout(account) -> dict:
  entry = {
    'id': "ETH",
    'symbol': "ETH",
    'name': "Ethereum",
    'native_balance': 0.0,
    'blockchain': "Arbitrum",
    'type': "EVM"
  }
  url = "https://arbitrum.blockscout.com/api"
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
    entry['native_balance'] = int(rjson['result']) * 10**-18
  return entry

def get_with_parameters(url,parameters,headers):

  session = Session()
  session.headers.update(headers)

  try:
    response = session.get(url, params=parameters)
  except (ConnectionError, Timeout, TooManyRedirects) as e:
    print(e)
  return response.json()

def convert_entry_from_decimals(entry):
  return int(entry['value']) * 10**-int(entry['token']['decimals'])

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
        'usd_balance': usd_balance,
        'blockchain': "Arbitrum",
        'type': "EVM",
        'exchange_rate': float(entry['token']['exchange_rate'])
      }
      #print(entries[id]['symbol']," : ",entries[id]['usd_balance'])
    else: continue
  return entries