from wallex import Token,solana,Wallet,base,Config, optimism, arbitrum, mantle,Scraper
import json

class WalletManager:
  mes_wallets: dict[str:Wallet.Tokens]
  tags: dict

  def __init__(self) -> None:
    self.config = Config.Config()
    self.mes_wallets = {}
    self.tags = self.config.load_file("tags.json")
    self.parsed_quotes = self.config.cmc.get_parsed_quotes(False)
    self.wallets_to_export = {}
    #patch: il faut que j'externalise les truc perso
    self.all_my_personnal_wallets = ['binance_sol', 'bybit_sol', 'cwsol', 'TELEGRAM', 'BITGET', 'CWDCA', 'custom_cwl', 'custom_phantom_sol','custom_binance_evm', 'custom_bybit_evm', 'custom_coinbasewallet']

  def add_cwl(self):
    c = self.config
    parsed_quotes = self.parsed_quotes
    cwl_base = base.get_tokens_balance_from_blockscout(c.evm_wallets['cwl'])
    cwl_optimism = optimism.get_tokens_balance_from_blockscout(c.evm_wallets['cwl'])
    cwl_arbitrum = arbitrum.get_tokens_balance_from_blockscout(c.evm_wallets['cwl'])
    cwl_mantle = mantle.get_tokens_balance_from_blockscout(c.evm_wallets['cwl'])
    cwl_base_native =base.get_native_balance_from_blockscout(c.evm_wallets['cwl'])
    cwl_optimism_native = optimism.get_native_balance_from_blockscout(c.evm_wallets['cwl'])
    cwl_arbitrum_native = arbitrum.get_native_balance_from_blockscout(c.evm_wallets['cwl'])
    cwl_mantle_native = mantle.get_native_balance_from_blockscout(c.evm_wallets['cwl'])

    mon_wallet = Wallet.Tokens()
    mon_wallet.add_json_entry(cwl_base_native)
    mon_wallet.add_json_entry(cwl_optimism_native)
    mon_wallet.add_json_entry(cwl_arbitrum_native)
    mon_wallet.add_json_entry(cwl_mantle_native)
    mon_wallet.add_json_entries(cwl_base)
    mon_wallet.add_json_entries(cwl_optimism)
    mon_wallet.add_json_entries(cwl_arbitrum)
    mon_wallet.add_json_entries(cwl_mantle)
    mon_wallet.name = "cwl"
    mon_wallet.update_all_exchange_rate_via_parsed_quotes(parsed_quotes)
    self.mes_wallets.update({mon_wallet.name:mon_wallet})

# Note pour plus tard penser à faire une fonction de remplacement du symbol lorsque l'on souhaite le moins populaire.
# certainenement à faire par blockchain et par wallet. Depuis le fichier de config ou un autre.
# exemple : 
# a_changer = {'VELO':'VELO_2', 'WBTC':'WBTC_2'}
#{token:{'id':obj['id'], 'name':obj['name'], 'contract_address':obj['contract_address'], 'native_balance':obj['native_balance'], 'usd_balance':obj['usd_balance'], 'blockchain':obj['blockchain'], 'type':obj['type'], 'exchange_rate':obj['exchange_rate'],'symbol':obj['symbol'] if obj['symbol'] not in a_changer.keys() else a_changer[obj['symbol']]}for token,obj in cwl_optimism.items()}
#{token:{'id':obj['id'], 'name':obj['name'],'symbol':obj['symbol'] if obj['symbol'] not in a_changer.keys() else a_changer[obj['symbol']], 'contract_address':obj['contract_address'], 'native_balance':obj['native_balance'], 'usd_balance':obj['usd_balance'], 'blockchain':obj['blockchain'], 'type':obj['type'], 'exchange_rate':obj['exchange_rate']}for token,obj in blockchain_result.items()}

  def fulfill_wallet(self):
    c = self.config
    parsed_quotes = self.parsed_quotes
    mes_wallets = {}
    # patch : symbol à changer pour moi mais à l'avenir j'aimerais que les doublons puissent etre decidé pour chaque blockchain depuis une interface.
    symbol_a_changer = {'VELO':'VELO_2'}
    changement = lambda blockchain_result,symbol_a_changer: {token:{'id':obj['id'] if obj['id'] not in symbol_a_changer.keys() else symbol_a_changer[obj['id']], 'name':obj['name'],'symbol':obj['symbol'] , 'contract_address':obj['contract_address'], 'native_balance':obj['native_balance'], 'usd_balance':obj['usd_balance'], 'blockchain':obj['blockchain'], 'type':obj['type'], 'exchange_rate':obj['exchange_rate']}for token,obj in blockchain_result.items()}
    for wallet in c.svm_wallets:
      mon_wallet = Wallet.Tokens(wallet)
      mon_wallet.add_json_entries(solana.get_spl_tokens_balance_from_moralis(c.moralis_api_key,c.svm_wallets[wallet]))
      mon_wallet.add_json_entry(solana.get_sol_balance_from_moralis(c.moralis_api_key,c.svm_wallets[wallet]))
      # un fake pyth casse mes stats. Je ne retire pas les scams des fois qu'ils pump sur un malentendu
      mon_wallet.remove_token_from_blockchain('PYTH','Solana')
      mon_wallet.update_all_exchange_rate_via_parsed_quotes(parsed_quotes)
      mes_wallets.update({wallet:mon_wallet})
    for wallet in c.evm_wallets:
      mon_wallet = Wallet.Tokens(wallet)
      # ici j'applique ce patch :-)
      blockchain = optimism.get_tokens_balance_from_blockscout(c.evm_wallets[wallet])
      print("apply changes to",wallet)
      try:
        blockchain = changement(blockchain,symbol_a_changer)
      except:
        print("failed:",wallet,blockchain)
      mon_wallet.add_json_entries(blockchain)
      mon_wallet.add_json_entries(arbitrum.get_tokens_balance_from_blockscout(c.evm_wallets[wallet]))
      mon_wallet.add_json_entries(mantle.get_tokens_balance_from_blockscout(c.evm_wallets[wallet]))
      mon_wallet.add_json_entries(base.get_tokens_balance_from_blockscout(c.evm_wallets[wallet]))
      mon_wallet.add_json_entry(arbitrum.get_native_balance_from_blockscout(c.evm_wallets[wallet]))
      mon_wallet.add_json_entry(optimism.get_native_balance_from_blockscout(c.evm_wallets[wallet]))
      mon_wallet.add_json_entry(mantle.get_native_balance_from_blockscout(c.evm_wallets[wallet]))
      mon_wallet.add_json_entry(base.get_native_balance_from_blockscout(c.evm_wallets[wallet]))
      mon_wallet.update_all_exchange_rate_via_parsed_quotes(parsed_quotes)
      mes_wallets.update({wallet:mon_wallet})

      self.mes_wallets = mes_wallets
    # chargement de la partie remplie off chain(non prise en charge par les API comme les lock/stack etc.)
    self.import_custom_wallets_from_json_file("custom_wallets_.json")
    self.fusion_wallets_by_name_1_2_in_3('cwl','CWL','custom_cwl')
    self.fusion_wallets_by_name_1_2_in_3('cwl','CWL','custom_cwl')
    self.fusion_wallets_by_name_1_2_in_3('phantom_sol','PHANTOM_SOL','custom_phantom_sol')
    self.fusion_wallets_by_name_1_2_in_3('binance_evm','BINANCE_EVM','custom_binance_evm')
    self.fusion_wallets_by_name_1_2_in_3('bybit_evm','BYBIT_EVM','custom_bybit_evm')
    self.fusion_wallets_by_name_1_2_in_3('coinbasewallet','COINBASEWALLET','custom_coinbasewallet')

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

  def get_tokens_by_strategie(self,strategie):
    resultat = {} 
    sum = self.get_global_summarized_tokens()
    for token in self.tags[strategie]['tokens']:
        if token in sum:
            resultat.update({token:round(sum[token],2)})
    return resultat

  def fusion_wallets_1_2_in_a_third_named(self,wallet1:Wallet.Tokens,wallet2:Wallet.Tokens,nom_wallet_final:str):
    #fusion
    wallet3 = Wallet.Tokens()
    for blockchain in wallet1.entries:
      wallet3.entries[blockchain] = {}
      w3 = wallet3.entries[blockchain]
      w1 = wallet1.entries[blockchain]
      if blockchain in wallet2.entries:
        #addition
        w2 = wallet2.entries[blockchain]
        for token in w1:
          if token in w2:
            for balance_type in ["native_balance","usd_balance"]:
              total = 0.0
              if hasattr(w1[token],balance_type) and hasattr(w2[token],balance_type):
                total = getattr(w1[token],balance_type) + getattr(w2[token],balance_type)
              elif hasattr(w1[token],balance_type):
                total = getattr(w1[token],balance_type)
              elif hasattr(w2[token],balance_type):
                total = getattr(w2[token],balance_type)
              if token not in w3:
                w3[token] = Token.Token(w1[token].get_json_entry())
              setattr(w3[token],balance_type,total)
          else:
            w3[token] = w1[token]
        for token in w2:
          if token not in w1:
            w3[token] = w2[token]
      else:
        for token in w1:
          w3[token] = Token.Token(w1[token].get_json_entry())
    for blockchain in wallet2.entries:
      w2 = wallet2.entries[blockchain]
      if blockchain not in wallet1.entries:
        wallet3.entries[blockchain] = {}
        w3 = wallet3.entries[blockchain]
        for token in w2:
          w3[token] = Token.Token(w2[token].get_json_entry())
    self.mes_wallets.update({nom_wallet_final:wallet3})
    return wallet3

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
      self.mes_wallets.update({mon_wallet.name:mon_wallet})

  def save_exported_wallets(self,filename="custom_wallets.json"):
    c = self.config
    c.save_to_file(filename,self.wallets_to_export)

  def get_list_wallets(self):
    return self.mes_wallets.keys()

  def save_my_personal_wallets(self):
    nom_wallet_cible = self.all_my_personnal_wallets
    for name in nom_wallet_cible:
      self.mes_wallets[name].name = name
      self.export_custom_wallet_as_json(self.mes_wallets[name])
    saved_wallets = self.save_exported_wallets("all_my_wallets.json")
    return saved_wallets

  def update_all_my_wallets(self):
    # patch: je dois imaginer un truc plus generique mais c'est juste le temps de travailler sur les charts, flemme de faire les updates manunellement a chaque fois
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

  def get_total_by_wallet(self):
    total_by_wallet = {}
    for wallet in self.mes_wallets:
      total_by_wallet.update({wallet:self.mes_wallets[wallet].sum_total_balance()})
    return total_by_wallet




