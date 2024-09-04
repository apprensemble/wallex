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


    

  def fulfill_wallet(self):
    c = self.config
    parsed_quotes = self.parsed_quotes
    mes_wallets = {}
    for wallet in c.svm_wallets:
      mon_wallet = Wallet.Tokens(wallet)
      mon_wallet.add_json_entries(solana.get_spl_tokens_balance_from_moralis(c.moralis_api_key,c.svm_wallets[wallet]))
      mon_wallet.add_json_entry(solana.get_sol_balance_from_moralis(c.moralis_api_key,c.svm_wallets[wallet]))
      mon_wallet.remove_token_from_blockchain('PYTH','Solana')
      #mon_wallet.update_all_missing_exchange_rate_via_parsed_quotes(parsed_quotes)
      mon_wallet.update_all_exchange_rate_via_parsed_quotes(parsed_quotes)
      mes_wallets.update({wallet:mon_wallet})
    for wallet in c.evm_wallets:
      mon_wallet = Wallet.Tokens(wallet)
      mon_wallet.add_json_entry(arbitrum.get_native_balance_from_blockscout(c.evm_wallets[wallet]))
      mon_wallet.add_json_entry(optimism.get_native_balance_from_blockscout(c.evm_wallets[wallet]))
      mon_wallet.add_json_entry(mantle.get_native_balance_from_blockscout(c.evm_wallets[wallet]))
      mon_wallet.add_json_entry(base.get_native_balance_from_blockscout(c.evm_wallets[wallet]))
      mon_wallet.add_json_entries(optimism.get_tokens_balance_from_blockscout(c.evm_wallets[wallet]))
      mon_wallet.add_json_entries(arbitrum.get_tokens_balance_from_blockscout(c.evm_wallets[wallet]))
      mon_wallet.add_json_entries(mantle.get_tokens_balance_from_blockscout(c.evm_wallets[wallet]))
      mon_wallet.add_json_entries(base.get_tokens_balance_from_blockscout(c.evm_wallets[wallet]))
      #mon_wallet.update_all_missing_exchange_rate_via_parsed_quotes(parsed_quotes)
      mon_wallet.update_all_exchange_rate_via_parsed_quotes(parsed_quotes)
      mes_wallets.update({wallet:mon_wallet})

      self.mes_wallets = mes_wallets

#    scraper = Scraper.Scraper()
#    #form btc entry from scrapping (temporary function)
#    items = scraper.get_history()
#    last_items = list(items.keys())[-1]
#    for wallet in c.btc_wallets:
#      btc = Token.Token({"id":"BTC","name":"Bitcoin","symbol":"BTC","native_balance":items[last_items][c.btc_wallets[wallet]],"type":"BTC","blockchain":"BTC"})
#      mes_wallets.update({"BTC":btc})
#    for wallet in c.egld_wallets:
#      egld = Token.Token({"id":"EGLD","name":"Elrond","symbol":"EGLD","native_balance":items[last_items][c.egld_wallets[wallet]],"type":"EGLD","blockchain":"MULTIVERSX"})
#      mes_wallets.update({"EGLD":egld})



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