from wallex import Token,solana,Wallet,Config,Scraper,zerion,mantle,Logger
import copy
import pandas as pd
import time

class WalletManager:
  mes_wallets: dict[str:Wallet.Tokens]
  tags: dict

  def __init__(self,mode_test=False) -> None:
    self.config = Config.Config()
    self.wallex_data_dir = self.config.wallex_common_data_dir
    self.config_dir = self.config.wallex_config_dir
    if mode_test:
      #mt pour mode test
      self.wallex_data_dir = self.config.wallex_common_data_dir_test
      self.config_dir = self.config.wallex_config_dir_test

    history_file = f"{self.wallex_data_dir}hf_api.json"
    self.tags_file = f"{self.wallex_data_dir}tags.json"
    self.tags = self.config.load_file(self.tags_file)
    self.ref_wallets_filename = f"{self.wallex_data_dir}ref_wallets.json"
    self.manual_wallets_filename = f"{self.wallex_data_dir}manual_wallets_.json"
    self.all_wallets_filename = f"{self.wallex_data_dir}all_my_wallets.json"
    self.csv_preparation_file = f"{self.config_dir}extra_position.txt"
    self.manual_tags_file = f"{self.config_dir}tags.json"
      

    self.history = Logger.Logger(history_file)
    self.mes_wallets = {}
    self.parsed_quotes = self.config.cmc.get_parsed_quotes(False)
    self.wallets_to_export = {}
    self.ref_wallets = {}
    try:
      self.import_ref_wallets_from_json_file()
    except:
      self.ref_wallets = {}
    #patch: il faut que j'externalise les truc perso
    self.all_my_personnal_wallets = ['binance_sol', 'bybit_sol', 'cwsol', 'coinbasewallet', 'manual_telegram', 'manual_bitget', 'manual_cwdca','manual_egld', 'custom_cwl', 'custom_phantom_sol','custom_binance_evm', 'custom_bybit_evm', 'manual_argentx','manual_subwallet']

  def call_refresh_quotes(self):
    self.parsed_quotes = self.config.cmc.get_parsed_quotes(True)

  def add_evm_wallet(self,account,name,refresh_quotes=False):
    parsed_quotes = self.parsed_quotes

    mon_wallet: Wallet.Tokens = zerion.get_evm_wallet(account,refresh_quotes)
    mon_wallet2: Wallet.Tokens = zerion.get_evm_complex_wallet(account,refresh_quotes)
    mon_wallet.name = name
    mon_wallet2.name = name
    if not mon_wallet.isInblockchain('Mantle'):
      mon_wallet.add_json_entry(mantle.get_native_balance_from_blockscout(account))
      mon_wallet.add_json_entries(mantle.get_tokens_balance_from_blockscout(account))
    mon_wallet3 = self.fusion_wallets_1_2_in_a_third_named(mon_wallet,mon_wallet2,name)
    mon_wallet3.change_symbol1_to_symbol2_on_blockchain_for_token_name('VELO','VELO2','Optimism','Velodrome')
    mon_wallet3.change_symbol1_to_symbol2_on_blockchain_for_complexe_token_name('VELO','VELO2','Optimism','Velodrome')
    mon_wallet3.update_all_missing_exchange_rate_via_parsed_quotes(parsed_quotes)
    self.update_tokens_datas_for_wallet_via_default_tags(mon_wallet3)
    self.mes_wallets.update({mon_wallet3.name:mon_wallet3})

  def add_svm_wallet(self,account,name,refresh_quotes=False):
    parsed_quotes = self.parsed_quotes
    mon_wallet = Wallet.Tokens(name)
    mon_wallet.add_json_entry(solana.get_sol_balance_from_moralis(self.config.moralis_api_key, account))
    mon_wallet.add_json_entries(solana.get_spl_tokens_balance_from_moralis(self.config.moralis_api_key, account))
    mon_wallet.remove_token_from_blockchain('PYTH','Solana')
    mon_wallet.change_symbol1_to_symbol2_on_blockchain_for_token_name('$WIF','WIF','Solana','dogwifhat')
    mon_wallet.update_all_missing_exchange_rate_via_parsed_quotes(parsed_quotes)
    self.update_tokens_datas_for_wallet_via_default_tags(mon_wallet)
    self.mes_wallets.update({mon_wallet.name:mon_wallet})

# Note pour plus tard penser à faire une fonction de remplacement du symbol lorsque l'on souhaite le moins populaire.
# certainenement à faire par blockchain et par wallet. Depuis le fichier de config ou un autre.
# exemple : 
# a_changer = {'VELO':'VELO2', 'WBTC':'WBTC2'}
#{token:{'id':obj['id'], 'name':obj['name'], 'contract_address':obj['contract_address'], 'native_balance':obj['native_balance'], 'usd_balance':obj['usd_balance'], 'blockchain':obj['blockchain'], 'type':obj['type'], 'exchange_rate':obj['exchange_rate'],'symbol':obj['symbol'] if obj['symbol'] not in a_changer.keys() else a_changer[obj['symbol']]}for token,obj in cwl_optimism.items()}
#{token:{'id':obj['id'], 'name':obj['name'],'symbol':obj['symbol'] if obj['symbol'] not in a_changer.keys() else a_changer[obj['symbol']], 'contract_address':obj['contract_address'], 'native_balance':obj['native_balance'], 'usd_balance':obj['usd_balance'], 'blockchain':obj['blockchain'], 'type':obj['type'], 'exchange_rate':obj['exchange_rate']}for token,obj in blockchain_result.items()}

  def fulfill_wallet_manager(self,refresh_quotes=False):
    c = self.config
    last_update = None 
    if refresh_quotes:
      self.call_refresh_quotes()
      last_update = time.time() 
    self.create_custom_tags_and_manual_wallets(last_update)
    for wallet in c.svm_wallets:
      self.add_svm_wallet(c.svm_wallets[wallet],wallet,refresh_quotes)
    for wallet in c.evm_wallets:
      #self.add_evm_wallet(c.evm_wallets[wallet],wallet,refresh_quotes)
      self.add_evm_wallet(c.evm_wallets[wallet],wallet,refresh_quotes)

    # chargement de la partie remplie off chain(non prise en charge par les API comme les lock/stack etc.)
    self.import_custom_wallets_from_json_file(self.manual_wallets_filename)
    self.fusion_wallets_by_name_1_2_in_3('cwl','manual_cwl','custom_cwl')
    self.fusion_wallets_by_name_1_2_in_3('phantom_sol','manual_phantom_sol','custom_phantom_sol')
    self.fusion_wallets_by_name_1_2_in_3('binance_evm','manual_binance_evm','custom_binance_evm')
    self.fusion_wallets_by_name_1_2_in_3('bybit_evm','manual_bybit_evm','custom_bybit_evm')
    #self.fusion_wallets_by_name_1_2_in_3('coinbasewallet','COINBASEWALLET','custom_coinbasewallet')
    self.update_all_my_wallets()
    self.remove_token_from_wallet_in_blockchain('ORCA','custom_phantom_sol','Solana')
    self.remove_token_from_wallet_in_blockchain('BLOOM','custom_cwl','Base')
    self.remove_token_from_wallet_in_blockchain('BOMB','custom_cwl','Base')
    self.compare_new_wallets_to_ref_wallets()
    self.save_my_personal_wallets()
    self.import_and_compare_custom_wallets_from_json_file(self.all_wallets_filename,from_scratch=True)
    #self.save_mes_wallets_as_ref_wallets(force_init_ref=True)
    self.get_total_by_wallet(True)

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
  
  def extract_real_symbol(self,long_symbol:str):
    symbol_composition = long_symbol.split("_")
    c_size = len(symbol_composition)
    real_symbol = symbol_composition[c_size-1]
    return real_symbol

  def get_strategie_names_for_token_in_strategie_tags(self,token_symbol:str,strategies: list):
    names = []
    for strategie in strategies:
      real_symbol = self.extract_real_symbol(token_symbol)
      if real_symbol in self.tags[strategie]['tokens']:
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
    #self.mes_wallets.update({new_wallet.name:new_wallet})
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

  def export_wallet_as_json(self,wallet:Wallet.Tokens):
    return {wallet.name:wallet.get_json_tokens_by_blockchain()}

  def export_wallet_as_json_(self,wallet:Wallet.Tokens):
    blockchains = {}
    for blockchain in wallet.get_list_blockchain():
      blockchains[blockchain] = {}
      for token in wallet.entries[blockchain]:
        entry: Token.Token = wallet.entries[blockchain][token]
        json_entry = entry.get_json_entry()
        blockchains[blockchain][token] = json_entry
    resultat = {wallet.name:blockchains}
    return resultat

  def export_ref_wallet_as_json(self,wallet:Wallet.Tokens):
    resultat = self.export_wallet_as_json(wallet)
    return resultat

  def export_custom_wallet_as_json(self,wallet:Wallet.Tokens):
    resultat = self.export_wallet_as_json(wallet)
    self.wallets_to_export.update(resultat)
    blockchains = resultat[wallet.name]
    return blockchains

  def import_and_compare_custom_wallets_from_json_file(self,filename="custom_wallets.json",from_scratch=False):
    if from_scratch:
      self.mes_wallets = {}
    self.import_custom_wallets_from_json_file(filename)
    self.compare_new_wallets_to_ref_wallets()
    #self.ref_wallets = self.save_mes_wallets_as_ref_wallets()

  def import_ref_wallets_from_json_file(self,filename=None):
    if not filename:
      filename = self.ref_wallets_filename
    wallets = self.config.load_file(filename)
    for wallet in wallets:
      mon_wallet = Wallet.Tokens()
      mon_wallet.add_json_entries_from_multi_blockchain(wallets[wallet])
      mon_wallet.name = wallet
      mon_wallet = self.update_tokens_datas_for_wallet_via_default_tags(mon_wallet)
      self.ref_wallets.update({mon_wallet.name:mon_wallet})

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

  def save_mes_wallets_as_ref_wallets(self,filename=None,force_init_ref=False):
    if len(self.mes_wallets) == 0:
      return self.ref_wallets
    nom_wallets_cible = self.mes_wallets.keys()
    saved_wallets = {}
    for name in nom_wallets_cible:
      self.mes_wallets[name].name = name
      self.mes_wallets[name].init_ref_values(force_init_ref)
      saved_wallets.update(self.export_ref_wallet_as_json(self.mes_wallets[name]))
      saved_wallets = saved_wallets.copy()
    if not filename:
      filename = self.ref_wallets_filename
    self.config.save_to_file(filename,saved_wallets)
    self.import_ref_wallets_from_json_file(filename)
    return saved_wallets

  def get_list_wallets(self):
    return list(self.mes_wallets.keys())

  def save_my_personal_wallets(self):
    nom_wallet_cible = self.all_my_personnal_wallets
    for name in nom_wallet_cible:
      self.mes_wallets[name].name = name
      self.export_custom_wallet_as_json(self.mes_wallets[name])
    saved_wallets = self.save_exported_wallets(self.all_wallets_filename)
    saved_wallets = self.save_exported_wallets(self.ref_wallets_filename)
    return saved_wallets

  def update_all_my_wallets(self,refresh_quotes=False,recover_updated_exchange_rate=False):
    # patch: je dois imaginer un truc plus generique mais c'est juste le temps de travailler sur les charts, flemme de faire les updates manunellement a chaque fois
    parsed_quotes = self.parsed_quotes
    nom_wallet_cible = self.all_my_personnal_wallets
    for name in nom_wallet_cible:
      if recover_updated_exchange_rate:
        self.mes_wallets[name].update_all_exchange_rate_via_parsed_quotes(parsed_quotes)
      else:
        self.mes_wallets[name].update_all_missing_exchange_rate_via_parsed_quotes(parsed_quotes)

  def update_all_exchange_rate_with_cmc(self,refresh_quotes=False):
    self.update_all_my_wallets(refresh_quotes,recover_updated_exchange_rate=True)

  def sum_all_wallets(self):
    total = 0
    total_by_tokens = self.get_global_summarized_tokens()
    for token in total_by_tokens:
      total += total_by_tokens[token]
    return total

  def get_total_by_wallet(self,write_history=False):
    total_by_wallet = {}
    for wallet in self.mes_wallets:
      total_by_wallet.update({wallet:self.mes_wallets[wallet].sum_total_balance()})
      if write_history:
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

  def convert_complete_csv_wallets_to_json_file_(self,input_filename,output_filename='wallet_from_csv.json',ref_date=time.time()):
    df = pd.read_csv(input_filename)
    wallets_from_csv = {}
    last_update = None
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
      origine = 'csv'
      if 'origine' in ligne:
        origine = ligne['origine']
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
      if 'last_update' in ligne:
        last_update = ligne['last_update']
      else:
        last_update = ref_date
      if origine == 'complexe':
        symbol = id_token.split("_")[-1]
        name = id_token.split("_")[0]
        id_token = f"{name}_{position}_{symbol}"
        origine = "csv_complexe"
      ref_native_balance = native_balance
      if 'ref_native_balance' in ligne:
        ref_native_balance = ligne['ref_native_balance']
      elif wallet in self.ref_wallets:
        iwallet: Wallet.Tokens = self.ref_wallets[wallet]
        if iwallet.get_detailled_token_infos_on_blockchain(id_token,blockchain):
          r = iwallet.get_detailled_token_infos_on_blockchain(id_token,blockchain)
          if 'ref_native_balance' in r:
            if str(r['ref_native_balance']).startswith("7.8770"):
              print(f"--------------------------------------->{r}")
              print(token)
              raise Exception("stop")
            ref_native_balance = r['ref_native_balance']

      if wallet not in wallets_from_csv:
        wallets_from_csv[wallet] = {}
      if blockchain not in wallets_from_csv[wallet]:
        wallets_from_csv[wallet][blockchain] = {}
      wallets_from_csv[wallet][blockchain].update({id_token:{ "id":id_token, "name":name, "symbol":id_token, "native_balance":native_balance, "exchange_rate":exchange_rate,"ref_exchange_rate":ref_exchange_rate,"ref_date_comparaison":ref_date_comparaison,"ref_native_balance":ref_native_balance, "usd_balance":usd_balance, "type":"Manuel", "blockchain":blockchain,"origine":origine,"famille":famille,"vision":vision,"strategie": strategie,"protocol":protocol,"position":position,"last_update":last_update }})
      self.config.save_to_file(output_filename,wallets_from_csv)

  def convert_complete_csv_wallets_to_json_file(self,input_filename,output_filename='wallet_from_csv.json',ref_date=time.time()):
    df = pd.read_csv(input_filename)
    wallets_from_csv = {}
    last_update = None
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
      origine = 'csv'
      if 'origine' in ligne:
        origine = ligne['origine']
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
      if 'last_update' in ligne:
        last_update = ligne['last_update']
      else:
        last_update = ref_date
      if origine == 'complexe':
        symbol = id_token.split("_")[-1]
        name = id_token.split("_")[0]
        id_token = f"{name}_{position}_{symbol}"
        origine = "csv_complexe"
      ref_native_balance = native_balance
      if 'ref_native_balance' in ligne:
        ref_native_balance = ligne['ref_native_balance']
      elif wallet in self.ref_wallets:
        iwallet: Wallet.Tokens = self.ref_wallets[wallet]
        if iwallet.get_detailled_token_infos_on_blockchain(id_token,blockchain):
          r = iwallet.get_detailled_token_infos_on_blockchain(id_token,blockchain)
          if 'ref_native_balance' in r:
            if str(r['ref_native_balance']).startswith("7.8770"):
              print(f"--------------------------------------->{r}")
              print(token)
              raise Exception("stop")
            ref_native_balance = r['ref_native_balance']



      if wallet not in wallets_from_csv:
        wallets_from_csv[wallet] = {}
      if blockchain not in wallets_from_csv[wallet]:
        wallets_from_csv[wallet][blockchain] = {}
      wallets_from_csv[wallet][blockchain].update({id_token:{ "id":id_token, "name":name, "symbol":id_token, "native_balance":native_balance, "exchange_rate":exchange_rate,"ref_exchange_rate":ref_exchange_rate,"ref_date_comparaison":ref_date_comparaison,"ref_native_balance":ref_native_balance, "usd_balance":usd_balance, "type":"Manuel", "blockchain":blockchain,"origine":origine,"famille":famille,"vision":vision,"strategie": strategie,"protocol":protocol,"position":position,"last_update":last_update }})
      self.config.save_to_file(output_filename,wallets_from_csv)

  def copy_wallet(self,name):
    if name in self.mes_wallets:
      old_wallet = copy.deepcopy(self.mes_wallets[name])
    elif f"custom_{name}" in self.mes_wallets:
      old_wallet = copy.deepcopy(self.mes_wallets[f"custom_{name}"])
    else:
      old_wallet = None
    return old_wallet

  def copy_old_wallets_and_import_new_wallets(self,filename):
    old_wallets = copy.deepcopy(self.mes_wallets)
    self.import_custom_wallets_from_json_file(filename)
    if old_wallets:
      for wallet in self.mes_wallets:
        new_wallet: Wallet.Tokens = self.mes_wallets[wallet]
        for blockchain in new_wallet.entries:
          for token in new_wallet.entries[blockchain]:
            if blockchain in old_wallets[wallet].entries:
              if token in old_wallets[wallet].entries[blockchain]:
                new_wallet.entries[blockchain][token].copy_ref_values(old_wallets[wallet].entries[blockchain][token]) 
    self.import_custom_wallets_from_json_file(filename)

  def compare_new_wallets_to_ref_wallets(self):
    if self.ref_wallets:
      ref_wallets = self.ref_wallets
      for wallet in self.mes_wallets:
        new_wallet: Wallet.Tokens = self.mes_wallets[wallet]
        if wallet in ref_wallets:
          if isinstance(ref_wallets[wallet],dict) :
            ref_wallet: Wallet.Tokens = Wallet.Tokens(wallet)
            ref_wallet.add_json_entries_from_multi_blockchain(self.ref_wallets[wallet])
            raise Exception("Hey ya un dict")
          else:
            ref_wallet: Wallet.Tokens = self.ref_wallets[wallet]
          for blockchain in new_wallet.get_list_blockchain():
            for token in new_wallet.get_list_tokens_on_blockchain(blockchain):
              if ref_wallet.get_token_on_blockchain(token,blockchain):
                ref_token = ref_wallet.get_token_on_blockchain(token,blockchain)
                new_wallet.update_ref_for_token_in_blockchain_with_token(blockchain,token,ref_token,force_init_ref=True) 
          self.mes_wallets.update({wallet:new_wallet})

  def generate_ref_wallets_from_csv(self,csv_file,ref_date):
    self.convert_complete_csv_wallets_to_json_file(csv_file,self.ref_wallets_filename,ref_date)
    self.import_custom_wallets_from_json_file(self.ref_wallets_filename)
    self.compare_new_wallets_to_ref_wallets()
    self.ref_wallets = copy.deepcopy(self.mes_wallets)

  def complete_ref_wallets(self,ref_wallets,mes_wallets):
    # instead of deep copy we add new entry and keeps older
    # encours
    for wallet in mes_wallets:
      if wallet in ref_wallets:
        ref_wallet: Wallet.Tokens = ref_wallets[wallet]
        mon_wallet: Wallet.Tokens = mes_wallets[wallet]
        for blockchain in mon_wallet.get_list_blockchain():
          if blockchain in ref_wallet.get_list_blockchain():
            for token in mon_wallet.get_list_tokens_on_blockchain(blockchain):
              if token in ref_wallet.get_list_tokens_on_blockchain(blockchain):
                ntoken: Token.Token = mon_wallet.get_token_on_blockchain(token,blockchain)
                  #ref_wallet.update_ref_token_on_blockchain(mon_wallet.get_token_on_blockchain(token,blockchain))
      else:
        ref_wallets[wallet] = mes_wallets[wallet]

  def copy_and_add_wallet(self,account,name,type_wallet,refresh_quote=False):
    old_wallet = self.copy_wallet(name)
    if type_wallet == 'EVM':
      self.add_evm_wallet(account,name,refresh_quote)
    elif type_wallet == 'SVM':
      self.add_svm_wallet(account,name,refresh_quote)
    if old_wallet:
      new_wallet: Wallet.Tokens = self.mes_wallets[name]
      for blockchain in new_wallet.entries:
        for token in new_wallet.entries[blockchain]:
          if blockchain in old_wallet.entries:
            if token in old_wallet.entries[blockchain]:
              new_wallet.entries[blockchain][token].copy_ref_values(old_wallet.entries[blockchain][token])

  def create_custom_tags_and_manual_wallets(self,last_update = None):
    wallex_common_data_dir = self.config.wallex_common_data_dir
    config_dir = self.config.wallex_config_dir
    csv_preparation_file = self.csv_preparation_file
    manual_tags_file = self.manual_tags_file
    auto_tags_file = self.tags_file
    manual_wallets_filename = self.manual_wallets_filename
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

    manual_wallet_file = {}
    for tags_,wallet,blockchain,token,native_balance,usd_balance,exchange_rate in resultat:
      wallet = 'manual_' + wallet.lower()
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
      if wallet in manual_wallet_file.keys():
        if blockchain in manual_wallet_file[wallet].keys():
          manual_wallet_file[wallet][blockchain].update({token:{ "id":token, "name":token, "symbol":token, "native_balance":native_balance, "exchange_rate":exchange_rate.split("\n")[0], "usd_balance":usd_balance, "type":"Manuel", "blockchain":blockchain,"origine":"manuelle","strategie": strategie,"protocol":protocol,"position":position ,"last_update":last_update}}) 
        else:
          manual_wallet_file[wallet][blockchain] = {
        token:{
          "id":token,
          "name":token,
          "symbol":token,
          "native_balance":native_balance,
          "exchange_rate":exchange_rate.split("\n")[0],
          "usd_balance":usd_balance,
          "last_update":last_update,
          "type":"Manuel",
          "blockchain":blockchain,
          "protocol": protocol,
          "position": position,
          "strategie": strategie,
          "origine": "manuelle" }}
      else:
        manual_wallet_file[wallet] = {
      blockchain:{
        token:{
          "id":token,
          "name":token,
          "symbol":token,
          "native_balance":native_balance,
          "exchange_rate":exchange_rate.split("\n")[0],
          "usd_balance":usd_balance,
          "last_update":last_update,
          "type":"Manuel",
          "blockchain":blockchain,
          "protocol": protocol,
          "position": position,
          "strategie": strategie,
          "origine": "manuelle"
    }}}
    self.config.save_to_file(manual_wallets_filename,manual_wallet_file)
    return manual_wallet_file 
