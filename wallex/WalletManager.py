from wallex import Token,solana,Wallet,Config,Scraper,zerion,mantle,Logger
import copy
import pandas as pd
import time

class WalletManager:
  mes_wallets: dict[str:Wallet.Tokens]
  tags: dict

  def __init__(self) -> None:
    self.config = Config.Config()
    self.wallex_data_dir = self.config.wallex_common_data_dir
    history_file = f"{self.wallex_data_dir}hf_api.json"
    self.history = Logger.Logger(history_file)
    self.mes_wallets = {}
    self.tags = self.config.load_file(f"{self.wallex_data_dir}tags.json")
    self.parsed_quotes = self.config.cmc.get_parsed_quotes(False)
    self.wallets_to_export = {}
    #patch: il faut que j'externalise les truc perso
    self.all_my_personnal_wallets = ['binance_sol', 'bybit_sol', 'cwsol', 'TELEGRAM', 'BITGET', 'CWDCA','EGLD', 'custom_cwl', 'custom_phantom_sol','custom_binance_evm', 'custom_bybit_evm', 'KEPLR','ARGENTX','SUBWALLET']

  def call_refresh_quotes(self):
    self.parsed_quotes = self.config.cmc.get_parsed_quotes(True)

  def add_evm_wallet(self,account,name,refresh_quotes=False):
    if refresh_quotes:
      self.call_refresh_quotes()
    parsed_quotes = self.parsed_quotes

    mon_wallet = zerion.get_evm_wallet(account,refresh_quotes)
    mon_wallet2 = zerion.get_evm_complex_wallet(account,refresh_quotes)
    mon_wallet.name = name
    mon_wallet2.name = name
    if 'Mantle' not in mon_wallet.entries.keys():
      mon_wallet.add_json_entry(mantle.get_native_balance_from_blockscout(account))
      mon_wallet.add_json_entries(mantle.get_tokens_balance_from_blockscout(account))
    mon_wallet3 = self.fusion_wallets_1_2_in_a_third_named(mon_wallet,mon_wallet2,name)
    mon_wallet3.change_symbol1_to_symbol2_on_blockchain_for_token_name('VELO','VELO2','Optimism','Velodrome')
    mon_wallet3.change_symbol1_to_symbol2_on_blockchain_for_complexe_token_name('VELO','VELO2','Optimism','Velodrome')
    mon_wallet3.update_all_exchange_rate_via_parsed_quotes(parsed_quotes)
    self.update_tokens_datas_for_wallet_via_default_tags(mon_wallet3)

  def add_svm_wallet(self,account,name,refresh_quotes=False):
    if refresh_quotes:
      self.call_refresh_quotes()
    parsed_quotes = self.parsed_quotes
    mon_wallet = Wallet.Tokens(name)
    mon_wallet.add_json_entry(solana.get_sol_balance_from_moralis(self.config.moralis_api_key, account))
    mon_wallet.add_json_entries(solana.get_spl_tokens_balance_from_moralis(self.config.moralis_api_key, account))
    mon_wallet.remove_token_from_blockchain('PYTH','Solana')
    mon_wallet.update_all_exchange_rate_via_parsed_quotes(parsed_quotes)
    self.update_tokens_datas_for_wallet_via_default_tags(mon_wallet)

# Note pour plus tard penser à faire une fonction de remplacement du symbol lorsque l'on souhaite le moins populaire.
# certainenement à faire par blockchain et par wallet. Depuis le fichier de config ou un autre.
# exemple : 
# a_changer = {'VELO':'VELO2', 'WBTC':'WBTC2'}
#{token:{'id':obj['id'], 'name':obj['name'], 'contract_address':obj['contract_address'], 'native_balance':obj['native_balance'], 'usd_balance':obj['usd_balance'], 'blockchain':obj['blockchain'], 'type':obj['type'], 'exchange_rate':obj['exchange_rate'],'symbol':obj['symbol'] if obj['symbol'] not in a_changer.keys() else a_changer[obj['symbol']]}for token,obj in cwl_optimism.items()}
#{token:{'id':obj['id'], 'name':obj['name'],'symbol':obj['symbol'] if obj['symbol'] not in a_changer.keys() else a_changer[obj['symbol']], 'contract_address':obj['contract_address'], 'native_balance':obj['native_balance'], 'usd_balance':obj['usd_balance'], 'blockchain':obj['blockchain'], 'type':obj['type'], 'exchange_rate':obj['exchange_rate']}for token,obj in blockchain_result.items()}

  def fulfill_wallet_manager(self,refresh_quotes=False):
    c = self.config
    self.create_custom_tags_and_custom_wallets()
    if refresh_quotes:
      self.call_refresh_quotes()
    for wallet in c.svm_wallets:
      self.call_add_svm_and_keep_ref_value(c.svm_wallets[wallet],wallet,refresh_quotes)
    for wallet in c.evm_wallets:
      #self.add_evm_wallet(c.evm_wallets[wallet],wallet,refresh_quotes)
      self.call_add_evm_and_keep_ref_value(c.evm_wallets[wallet],wallet,refresh_quotes)

    # chargement de la partie remplie off chain(non prise en charge par les API comme les lock/stack etc.)
    self.import_custom_wallets_from_json_file(f"{self.wallex_data_dir}custom_wallets_.json")
    self.fusion_wallets_by_name_1_2_in_3('cwl','CWL','custom_cwl')
    self.fusion_wallets_by_name_1_2_in_3('phantom_sol','PHANTOM_SOL','custom_phantom_sol')
    self.fusion_wallets_by_name_1_2_in_3('binance_evm','BINANCE_EVM','custom_binance_evm')
    self.fusion_wallets_by_name_1_2_in_3('bybit_evm','BYBIT_EVM','custom_bybit_evm')
    #self.fusion_wallets_by_name_1_2_in_3('coinbasewallet','COINBASEWALLET','custom_coinbasewallet')
    self.update_all_my_wallets()
    self.remove_token_from_wallet_in_blockchain('ORCA','custom_phantom_sol','Solana')
    self.remove_token_from_wallet_in_blockchain('BLOOM','custom_cwl','Base')
    self.remove_token_from_wallet_in_blockchain('BOMB','custom_cwl','Base')
    self.save_my_personal_wallets()
    self.mes_wallets = {}
    self.import_custom_wallets_from_json_file(f"{self.wallex_data_dir}all_my_wallets.json")
    self.get_total_by_wallet()

  def launch_new_scrapping(self):
    scraper = Scraper.Scraper()
    c = self.config
    scraper.get_balances_evm_from_debank(c.evm_wallets)
    scraper = Scraper.Scraper()
    scraper.get_balances_solana_from_solscan(c.svm_wallets)
    scraper = Scraper.Scraper()
    scraper.get_balances_multivers_from_explorer(c.config_file['public_keys']['egld'])
    scraper = Scraper.Scraper()
    scraper.get_balances_bitcoin_from_mempool(c.config_file['public_keys']['btc'])
    self.scraper = Scraper.Scraper()

  def is_token_in_strategie_tag(self,token_symbol:str,strategie:str):
    if token_symbol in self.tags[strategie]['tokens']:
      return True
    else:
      return False
  
  def is_token_in_strategie_tags(self,token_symbol:str,strategies: list):
    for strategie in strategies:
      if token_symbol in self.tags[strategie]['tokens']:
        return True
      else:
        return False

  def get_strategie_names_for_token_in_strategie_tags(self,token_symbol:str,strategies: list):
    names = []
    for strategie in strategies:
      if token_symbol in self.tags[strategie]['tokens']:
        names.append(strategie)
    return names




  def get_tokens_by_strategie_for_specified_wallet(self,strategie,wallet:Wallet.Tokens):
    resultat = []
    mon_wallet = wallet
    sum = mon_wallet.get_detailled_balance_by_summarized_token()
    for token in self.tags[strategie]['tokens']:
        if token in sum:
            resultat.append({token:round(sum[token],2)})
    return resultat

  def get_global_summarized_tokens(self):
    sums = {}
    for wallet in self.mes_wallets:
      sum = self.mes_wallets[wallet].get_detailled_balance_by_summarized_token()
      for token in sum:
        if token in sums:
          sums[token] += sum[token]
        else:
          sums[token] = sum[token]
    sums = dict(sorted(sums.items(), key=lambda item: item[1],reverse=True))
    return sums

  def get_tokens_by_blockchain(self):
    resultat = {}
    for wallet in self.mes_wallets:
      w = self.mes_wallets[wallet].get_detailled_balance_by_blockchain()
      for bc in w:
        for wbc in w[bc]:
          for token in wbc:
            if bc in resultat and token in resultat[bc]:
              resultat[bc][token] += wbc[token]
            elif bc in resultat:
              resultat[bc][token] = wbc[token]
            else:
              resultat[bc] = {}
              resultat[bc][token] = wbc[token]
            rbc = resultat[bc]
            resultat[bc] = dict(sorted(rbc.items(), key=lambda item: item[1],reverse=True))
    return resultat

  def get_tokens_by_strategie(self,strategie):
    resultat = {} 
    sum = self.get_global_summarized_tokens()
    for token in self.tags[strategie]['tokens']:
        if token in sum:
            resultat.update({token:round(sum[token],2)})
    return resultat

  def update_tokens_datas_for_wallet_via_default_tags(self,wallet:Wallet.Tokens):
    jwallet = wallet.get_detailled_tokens_infos_by_blockchain()
    new_wallet = Wallet.Tokens()
    for bc in jwallet:
      for tokens in jwallet[bc]:
          for token in tokens.keys():
            if self.is_token_in_strategie_tag(token,"hold"):
              tokens[token]['vision'] = 'hold'
            else:
              tokens[token]['vision'] = 'trade'
            famille = self.get_strategie_names_for_token_in_strategie_tags(token,['BTC','ETH','SOL','stablecoin'])
            if len(famille) > 1:
              tokens[token]['famille'] = 'famille_multiple'
            elif len(famille) == 0:
              tokens[token]['famille'] = 'autre'
            else:
              tokens[token]['famille'] = famille.pop()
            if 'protocol' in tokens[token]:
              if tokens[token]['protocol'] != "libre":
                tokens[token]['strategie'] = 'invested'
              elif (tokens[token]['vision'] != 'trade' or tokens[token]['famille'] != 'autre' or self.is_token_in_strategie_tag(token,"suivi")):
                tokens[token]['strategie'] = 'suivi'
              else:
                tokens[token]['strategie'] = 'non_suivi'
            else:
              tokens[token]['protocol'] = 'protocol_oublié'
            new_wallet.add_json_entry(tokens[token])
    new_wallet.name = wallet.name
    self.mes_wallets.update({new_wallet.name:new_wallet})
    return new_wallet


  def fusion_wallets_1_2_in_a_third_named(self,wallet1:Wallet.Tokens,wallet2:Wallet.Tokens,nom_wallet_final:str):
    jwallet1 = wallet1.get_detailled_tokens_infos_by_blockchain()
    jwallet2 = wallet2.get_detailled_tokens_infos_by_blockchain()
    mon_wallet = Wallet.Tokens()
    for bc in jwallet1:
      for tokens in jwallet1[bc]:
          for token in tokens.keys():
            mon_wallet.add_json_entry(tokens[token])
    for bc in jwallet2:
      for tokens in jwallet2[bc]:
          for token in tokens.keys():
            mon_wallet.add_json_entry(tokens[token])
    mon_wallet.name = nom_wallet_final
    self.mes_wallets.update({nom_wallet_final:mon_wallet})
    return mon_wallet

  def fusion_wallets_by_name_1_2_in_3(self,first:str,second:str,name_of_the_result:str):
    w1 = self.mes_wallets[first]
    w2 = self.mes_wallets[second]
    w3 = self.fusion_wallets_1_2_in_a_third_named(w1,w2,name_of_the_result)
    return w3

  def export_custom_wallet_as_json(self,wallet:Wallet.Tokens):
    blockchains = {}
    for blockchain in wallet.entries:
      blockchains[blockchain] = {}
      for token in wallet.entries[blockchain]:
        entry: Token.Token = wallet.entries[blockchain][token]
        json_entry = entry.get_json_entry()
        blockchains[blockchain][token] = json_entry
    resultat = {wallet.name:blockchains}
    self.wallets_to_export.update(resultat)
    return blockchains

  def import_custom_wallets_from_json_file(self,filename="custom_wallets.json"):
    wallets = self.config.load_file(filename)
    for wallet in wallets:
      mon_wallet = Wallet.Tokens()
      mon_wallet.add_json_entries_from_multi_blockchain(wallets[wallet])
      mon_wallet.name = wallet
      mon_wallet = self.update_tokens_datas_for_wallet_via_default_tags(mon_wallet)
      self.mes_wallets.update({mon_wallet.name:mon_wallet})

  def save_exported_wallets(self,filename="custom_wallets.json"):
    c = self.config
    c.save_to_file(filename,self.wallets_to_export)

  def get_list_wallets(self):
    return list(self.mes_wallets.keys())

  def save_my_personal_wallets(self):
    nom_wallet_cible = self.all_my_personnal_wallets
    for name in nom_wallet_cible:
      self.mes_wallets[name].name = name
      self.export_custom_wallet_as_json(self.mes_wallets[name])
    saved_wallets = self.save_exported_wallets(f"{self.wallex_data_dir}all_my_wallets.json")
    return saved_wallets

  def update_all_my_wallets(self,refresh_quotes=False):
    # patch: je dois imaginer un truc plus generique mais c'est juste le temps de travailler sur les charts, flemme de faire les updates manunellement a chaque fois
    if refresh_quotes:
      self.call_refresh_quotes()
    parsed_quotes = self.parsed_quotes
    nom_wallet_cible = self.all_my_personnal_wallets
    for name in nom_wallet_cible:
      self.mes_wallets[name].update_all_exchange_rate_via_parsed_quotes(parsed_quotes)

  def sum_all_wallets(self):
    total = 0
    total_by_tokens = self.get_global_summarized_tokens()
    for token in total_by_tokens:
      total += total_by_tokens[token]
    return total

  def get_total_by_wallet(self,write_hitory=False):
    total_by_wallet = {}
    for wallet in self.mes_wallets:
      total_by_wallet.update({wallet:self.mes_wallets[wallet].sum_total_balance()})
      if write_hitory:
        self.history.add_content({wallet:self.mes_wallets[wallet].sum_total_balance()})
    return total_by_wallet

  def remove_token_from_wallet_in_blockchain(self,token,wallet,blockchain):
    try:
      mon_wallet = self.mes_wallets[wallet]
      mon_wallet.remove_token_from_blockchain(token,blockchain)
    except Exception as e:
      print(e)

  def get_flexible_tags(self,tags_list:list=[]):
    flexible_tags = {}
    for s in tags_list:
      flexible_tags.update({s:sum(self.get_tokens_by_strategie(s).values())})
    return flexible_tags


  def get_portfolio_composition_by_type(self):
    tokens_suivi = []
    hold = sum(self.get_tokens_by_strategie("hold").values())
    tokens_suivi.extend(list(self.get_tokens_by_strategie("hold").keys()))
    flexible_tags = 0
    for s in self.get_flexible_tags().keys():
      categories = self.get_tokens_by_strategie(s)
      flexible_tags +=  sum(categories.values())
      tokens_suivi.extend(list(categories.keys()))
    step = self.get_tokens_by_strategie("locked")
    locked = sum(step.values())
    tokens_suivi.extend(list(step.keys()))
    step = self.get_tokens_by_strategie("stablecoin")
    stablecoin = sum(step.values())
    tokens_suivi.extend(list(step.keys()))
    # est consideré non suivi ce qui n'est dans aucune des categories au dessus
    non_suivi = 0
    all_tokens = self.get_global_summarized_tokens()
    for token in all_tokens:
      if token not in tokens_suivi:
        non_suivi += all_tokens[token]
    resultat = {'hold':hold,'flexible_tags':flexible_tags,'locked':locked,'stablecoin':stablecoin,'non_suvi':round(non_suivi,2)}
    return resultat

  def get_tokens_non_suivi(self):
    # liste des tokens suivis
    lts = []
    tokens_non_suivi = {}
    # la famille des tokens suivis est hold, locked, stablecoin et flexible yield.
    for f in ['hold','flexible_tags','locked','stablecoin']:
      if f == 'flexible_tags':
        for g in list(self.get_flexible_tags().keys()):
          lts.extend(list(self.get_tokens_by_strategie(g).keys()))
      else:
        lts.extend(list(self.get_tokens_by_strategie(f).keys()))
    all_tokens = self.get_global_summarized_tokens()
    for token in all_tokens:
      if token not in lts:
        tokens_non_suivi[token] = all_tokens[token]
    return tokens_non_suivi

  def get_wallets(self):
    resultat = {}
    for wallet in self.mes_wallets:
      resultat.update({wallet:self.mes_wallets[wallet].get_detailled_tokens_infos_by_blockchain()})
    return resultat

  def convert_complete_csv_wallets_to_json_file(self,input_filename,output_filename='wallet_from_csv.json',ref_date=time.time()):
    df = pd.read_csv(input_filename)
    wallets_from_csv = {}
    for i,ligne in df.iterrows():
      wallet = ligne['wallet']
      blockchain = ligne['bc']
      token = ligne['token']
      if 'id_token' in ligne:
        id_token = ligne['id_token']
      else:
        id_token = token
      if 'token_full_name' in ligne:
        name = ligne['token_full_name']
      else:
        name = token
      exchange_rate = ligne['exchange_rate']
      native_balance = ligne['native_balance']
      usd_balance = ligne['usd_balance']
      famille = ligne['famille']
      strategie = ligne['strategie']
      vision = ligne['vision']
      origine = "csv"
      position = ligne['position']
      if 'protocol' in ligne:
        protocol = ligne['protocol']
      else:
        protocol = 'A DEFINIR'
      if 'ref_exchange_rate' in ligne:
        ref_exchange_rate = ligne['ref_exchange_rate']
      else:
        ref_exchange_rate = exchange_rate
      if 'ref_date_comparaison' in ligne:
        ref_date_comparaison = ligne['ref_date_comparaison']
      else:
        ref_date_comparaison = ref_date



      if wallet not in wallets_from_csv:
        wallets_from_csv[wallet] = {}
      if blockchain not in wallets_from_csv[wallet]:
        wallets_from_csv[wallet][blockchain] = {}
      wallets_from_csv[wallet][blockchain].update({token:{ "id":id_token, "name":name, "symbol":token, "native_balance":native_balance, "exchange_rate":exchange_rate,"ref_exchange_rate":ref_exchange_rate,"ref_date_comparaison":ref_date_comparaison, "usd_balance":usd_balance, "type":"Custom", "blockchain":blockchain,"origine":origine,"famille":famille,"vision":vision,"strategie": strategie,"protocol":protocol,"position":position }})
      self.config.save_to_file(output_filename,wallets_from_csv)


  def call_add_evm_and_keep_ref_value(self,account,name,refresh_quote=False):
    if name in self.mes_wallets:
      old_wallet = copy.deepcopy(self.mes_wallets[name])
    elif f"custom_{name}" in self.mes_wallets:
      old_wallet = copy.deepcopy(self.mes_wallets[f"custom_{name}"])
    else:
      old_wallet = None
    self.add_evm_wallet(account,name,refresh_quote)
    if old_wallet:
      new_wallet: Wallet.Tokens = self.mes_wallets[name]
      for blockchain in new_wallet.entries:
        for token in new_wallet.entries[blockchain]:
          if blockchain in old_wallet.entries:
            if token in old_wallet.entries[blockchain]:
              new_wallet.entries[blockchain][token].copy_ref_values(old_wallet.entries[blockchain][token])

  def call_add_svm_and_keep_ref_value(self,account,name,refresh_quote=False):
    if name in self.mes_wallets:
      old_wallet = copy.deepcopy(self.mes_wallets[name])
    elif f"custom_{name}" in self.mes_wallets:
      old_wallet = copy.deepcopy(self.mes_wallets[f"custom_{name}"])
    else:
      old_wallet = None
    self.add_svm_wallet(account,name,refresh_quote)
    if old_wallet:
      new_wallet: Wallet.Tokens = self.mes_wallets[name]
      for blockchain in new_wallet.entries:
        for token in new_wallet.entries[blockchain]:
          if blockchain in old_wallet.entries:
            if token in old_wallet.entries[blockchain]:
              new_wallet.entries[blockchain][token].copy_ref_values(old_wallet.entries[blockchain][token])



    

  def create_custom_tags_and_custom_wallets(self):
    wallex_common_data_dir = self.config.wallex_common_data_dir
    config_dir = self.config.wallex_config_dir
    csv_preparation_file = f"{config_dir}extra_position.txt"
    manual_tags_file = f"{config_dir}tags.json"
    auto_tags_file = f"{wallex_common_data_dir}tags.json"
    custom_wallets_filename = f"{wallex_common_data_dir}custom_wallets_.json"
    resultat = [[x for x in line.split(":")] for line in open(csv_preparation_file) if len(line) > 1 and "#" not in line]

    tags = self.config.load_file(manual_tags_file)
    tags = {tag:token['tokens'] for tag,token in tags.items()}
    for line in resultat:
      a = {x.lower():[line[3]] for x in line[0].split("_")}
      for (tag,token) in a.items():
        if tag in tags.keys():
          tags[tag].append(token[0])
        else:
          tags[tag] = token

    tag_file = { title:{"nom": title, "kind":"strategie", "description":"blabla",
                    "tokens":list(set(tokens))} for (title,tokens) in tags.items()}

    self.config.save_to_file(auto_tags_file,tag_file)

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
    self.config.save_to_file(custom_wallets_filename,custom_wallet_file)
    return custom_wallet_file 
