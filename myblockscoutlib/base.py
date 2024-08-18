from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects

def get_token_balances_from_blockscout(account):
  url_suffixe = "/addresses/"+account+"/token-balances"
  url = "https://base.blockscout.com/api/v2" + url_suffixe
  parameters = {
  }
  headers = {
    'Accepts': 'application/json'
  }
  return get_with_parameters(url,parameters,headers)

def get_native_balances_from_blockscout(account):
  entry = {
    'id': "ETH",
    'symbol': "ETH",
    'name': "Ethereum",
    'native_balance': 0.0
  }
  url = "https://base.blockscout.com/api"
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

def parse_response_from_blockscout(rjson,quotes):
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
        'native_balance': entry['value'],
        'usd_balance': usd_balance,
        'exchange_rate': entry['token']['exchange_rate']
      }
      print(entries[id]['symbol']," : ",entries[id]['usd_balance'])
    else: continue
  return entries

def sum_tokens_usd_balances(entries):
  total: float = 0.0
  for indice in entries:
    print(entries[indice]," ", entries[indice]['usd_balance'])
    total += entries[indice]['usd_balance']
  return total

def update_exchange_rate_to_entry(entry,exhange_rate):
  old_usd_balance = 0.0
  entry['exchange_rate'] = exhange_rate
  new_usd_balance = round(entry['native_balance'] * entry['exchange_rate'],2)
  if 'usd_balance' in entry.keys():
    old_usd_balance = entry['usd_balance'] 
  entry['usd_balance'] = new_usd_balance 
  print("usd balance updated from ",old_usd_balance," to ",new_usd_balance)
  return entry