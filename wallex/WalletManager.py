from wallex import Token,solana,Wallet,base,Config, optimism, arbitrum, mantle,Scraper

class WalletManager:
  mes_wallets: dict[str:Wallet.Tokens]
  tags: dict

  def __init__(self) -> None:
    self.config = Config.Config()
    self.mes_wallets = {}
    self.tags = self.config.load_file("tags.json")
    self.parsed_quotes = self.config.cmc.get_parsed_quotes(False)

  def fulfill_wallet(self):
    c = self.config
    parsed_quotes = self.parsed_quotes
    mes_wallets = {}
    for wallet in c.svm_wallets:
      mon_wallet = Wallet.Tokens()
      mon_wallet.add_json_entries(solana.get_spl_tokens_balance_from_moralis(c.moralis_api_key,c.svm_wallets[wallet]))
      mon_wallet.add_json_entry(solana.get_sol_balance_from_moralis(c.moralis_api_key,c.svm_wallets[wallet]))
      mon_wallet.remove_token_from_blockchain('PYTH','Solana')
      mon_wallet.update_all_missing_exchange_rate_via_parsed_quotes(parsed_quotes)
      mes_wallets.update({wallet:mon_wallet})
    for wallet in c.evm_wallets:
      mon_wallet = Wallet.Tokens()
      mon_wallet.add_json_entry(arbitrum.get_native_balance_from_blockscout(c.evm_wallets[wallet]))
      mon_wallet.add_json_entry(optimism.get_native_balance_from_blockscout(c.evm_wallets[wallet]))
      mon_wallet.add_json_entry(mantle.get_native_balance_from_blockscout(c.evm_wallets[wallet]))
      mon_wallet.add_json_entry(base.get_native_balance_from_blockscout(c.evm_wallets[wallet]))
      mon_wallet.add_json_entries(optimism.get_tokens_balance_from_blockscout(c.evm_wallets[wallet]))
      mon_wallet.add_json_entries(arbitrum.get_tokens_balance_from_blockscout(c.evm_wallets[wallet]))
      mon_wallet.add_json_entries(mantle.get_tokens_balance_from_blockscout(c.evm_wallets[wallet]))
      mon_wallet.add_json_entries(base.get_tokens_balance_from_blockscout(c.evm_wallets[wallet]))
      mon_wallet.update_all_missing_exchange_rate_via_parsed_quotes(parsed_quotes)
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


