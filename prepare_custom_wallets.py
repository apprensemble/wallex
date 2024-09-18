#!.venv/bin/python
from wallex import Config

c = Config.Config()
wallex_common_data_dir = c.wallex_common_data_dir
config_dir = c.wallex_config_dir
csv_preparation_file = f"{config_dir}extra_position.txt"
manual_tags_file = f"{config_dir}tags.json"
auto_tags_file = f"{wallex_common_data_dir}tags.json"
custom_wallets_file = f"{wallex_common_data_dir}custom_wallets_.json"
resultat = [[x for x in line.split(":")] for line in open(csv_preparation_file) if len(line) > 1 and "#" not in line]
def create_tags_file(filename):
  #take lines

  #parse tags
  #{x:resultat[0][3] for x in resultat[0][0].split("_")}
  #{'TAG1': 'NOMDEX_TOKEN1_TOKEN2_TOKENX', 'TAG2': 'NOMDEX_TOKEN1_TOKEN2_TOKENX'}

  tags = c.load_file(manual_tags_file)
  tags = {tag:token['tokens'] for tag,token in tags.items()}
  for line in resultat:
    a = {x.lower():[line[3]] for x in line[0].split("_")}
    for (tag,token) in a.items():
      if tag in tags.keys():
        tags[tag].append(token[0])
      else:
        tags[tag] = token

  #{'TAG1': ['NOMDEX_TOKEN1_TOKEN2_TOKENX'], 
  # 'TAG2': ['NOMDEX_TOKEN1_TOKEN2_TOKENX'], 
  # 'LPC': ['BEEFY_USDC+_USD+', 'BEEFY_OVN_USD+', 
  # 'BEEFY_SONNE_USDC', 'BEEFY_USD+_FRAX_USDC','BEEFY_GMX', 'BEEFY_SONNE_USDC'], 
  # 'LP': ['AERODROME_USDC_USD+', 'AERODROME_ETH_FBOMB'], 
  # 'LOCKED': ['AERO', 'VELO', 'JUP'], 'FARMING': ['BEEFY_CBETH_WETH', 'ORCA_JUP_USDC'], 'STACKING': ['ARBDOGE_AIDOGE', 'ABR', 'ETH'], 'TOKEN': ['MKR', 'BTCB', 'BNB'], 'HOLD': ['TON', 'NOT', 'NOT', 'TON', 'TON', 'BTC'], 'NOTSCRAPED': ['TON', 'NOT', 'NOT', 'TON', 'TON', 'JUP', 'ORCA_JUP_USDC'], 'CEX': ['TON']}

  tag_file = { title:{"nom": title, "kind":"strategie", "description":"blabla",
                  "tokens":list(set(tokens))} for (title,tokens) in tags.items()}

  c.save_to_file(filename,tag_file)
  return tag_file

def create_custom_wallets_file(filename):

  custom_wallet_file = {}
  for tags_,wallet,blockchain,token,native_balance,usd_balance,exchange_rate in resultat:
    tags = tags_.split("_")
    protocol = 'libre'
    position = "wallet"
    if len(token.split("_")) > 2:
      protocol = token.split("_")[0]
      strategie = "invested"
      position = "deposit"
    elif len(token.split("_")) > 1:
      protocol = token.split("_")[0]
      strategie = "invested"
      position = "staked"
    elif "TOKEN" in tags and len(tags) < 2:
      strategie = "non_suivi"
    else:
      strategie = "suivi"
    blockchain = blockchain.capitalize()
    if wallet in custom_wallet_file.keys():
      if blockchain in custom_wallet_file[wallet].keys():
        custom_wallet_file[wallet][blockchain].update({token:{ "id":token, "name":token, "symbol":token, "native_balance":native_balance, "exchange_rate":exchange_rate.split("\n")[0], "usd_balance":usd_balance, "type":"Custom", "blockchain":blockchain,"origine":"manuelle","strategie": strategie,"protocol":protocol,"position":position }}) 
      else:
        custom_wallet_file[wallet][blockchain] = {
      token:{
        "id":token,
        "name":token,
        "symbol":token,
        "native_balance":native_balance,
        "exchange_rate":exchange_rate.split("\n")[0],
        "usd_balance":usd_balance,
        "type":"Custom",
        "blockchain":blockchain,
        "protocol": protocol,
        "position": position,
        "strategie": strategie,
        "origine": "manuelle" }}
    else:
      custom_wallet_file[wallet] = {
    blockchain:{
      token:{
        "id":token,
        "name":token,
        "symbol":token,
        "native_balance":native_balance,
        "exchange_rate":exchange_rate.split("\n")[0],
        "usd_balance":usd_balance,
        "type":"Custom",
        "blockchain":blockchain,
        "protocol": protocol,
        "position": position,
        "strategie": strategie,
        "origine": "manuelle"
  }}}
  c.save_to_file(filename,custom_wallet_file)
  return custom_wallet_file 

create_tags_file(auto_tags_file)
create_custom_wallets_file(custom_wallets_file)