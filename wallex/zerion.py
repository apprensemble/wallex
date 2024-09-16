from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from wallex import Config,Wallet
import os.path

c = Config.Config()
zerion_api_key = c.zerion_api_key
data_dir = c.wallex_common_data_dir
# fichier de stockage en attendant une bdd( pour reduire les appels)

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
    print(response)
    print(response.json()['errors'])
    return {}

def parse_response_and_return_wallet(rjson,origine="simple"):
  mon_wallet = Wallet.Tokens()
  for token in rjson:
    try:
      exchange_rate = float(token['attributes']['price'])
      native_balance = float(token['attributes']['quantity']['float'])
      if exchange_rate > 0:
        usd_balance = round(float(token['attributes']['value']),2)
      else:
        usd_balance = 0.0
      blockchain = token['relationships']['chain']['data']['id']
      if origine == "complexe":
        name = token['attributes']['name']
        symbol = token['attributes']['fungible_info']['symbol'] 
        symbol = f"{name}_{symbol}"
      else:
        name = token['attributes']['fungible_info']['name']
        symbol = token['attributes']['fungible_info']['symbol'] 
      position = token['attributes']['position_type']
      protocol = token['attributes']['protocol']
      if not protocol:
        protocol = 'libre'
      # AVAX et WAVAX ont le symbol AVAX sur zerion
      if blockchain.capitalize() == 'Binance-smart-chain':
        blockchain = "BNB"
      if name == 'Wrapped AVAX':
        symbol = "WAVAX"
      if name.find("ApeSwap") > -1:
        symbol = "BANANA2"
      entry = {
        'id': symbol,
        'name': name,
        'symbol': symbol,
        'contract_address': token['id'].split("-")[0],
        'native_balance': native_balance,
        'usd_balance': usd_balance,
        'blockchain': blockchain.capitalize(),
        'origine': origine,
        'type': "EVM",
        'exchange_rate': exchange_rate,
        'position': position,
        'protocol': protocol
      }
      mon_wallet.add_json_entry(entry)
    except Exception as e:
      print(token['attributes']['fungible_info']['symbol'],e)
      continue
  return mon_wallet

def get_evm_wallet(account,refresh=False,positions="only_simple"):
  refresh_file = f"{data_dir}zerion_{positions}_{account}.json"
  resultat = {}
  url_suffixe = account+"/positions/?filter[positions]="+positions+"&currency=usd&filter[trash]=only_non_trash&sort=value"
  url = "https://api.zerion.io/v1/wallets/" + url_suffixe
  parameters = {
  }
  headers = {
    'Accepts': 'application/json',
    "authorization": "Basic "+zerion_api_key
  }
  if refresh:
    rjson =  get_with_parameters(url,parameters,headers)
  elif os.path.isfile(refresh_file):
    rjson = c.load_file(refresh_file)
  else:
    refresh = True
    rjson =  get_with_parameters(url,parameters,headers)
  if 'data' in rjson and refresh:
    c.save_to_file(refresh_file,rjson)
  elif 'data' not in rjson:
    raise Exception(f"no data for {account} {rjson}")
  if positions == "only_simple":
    resultat = parse_response_and_return_wallet(rjson['data'])
  else:
    resultat = parse_response_and_return_wallet(rjson['data'],"complexe")
  return resultat

def get_evm_complex_wallet(account,refresh=False):
  resultat = get_evm_wallet(account,refresh,"only_complex")
  return resultat