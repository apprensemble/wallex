#!/home/grillon/Documents/Exercices/wallex/.venv/bin/python
from wallex import Token,solana,Wallet,base,Config, optimism, arbitrum, mantle
from importlib import reload

c = Config.Config()
mon_wallet = Wallet.Tokens()
parsed_quotes = c.cmc.get_parsed_quotes(False)
from wallex import Scraper
scraper = Scraper.Scraper()

scraper.get_balances_evm_from_debank(c.evm_wallets)
scraper = Scraper.Scraper()
scraper.get_balances_solana_from_solscan(c.svm_wallets)
scraper = Scraper.Scraper()
scraper.get_balances_multivers_from_explorer(c.config_file['public_keys']['egld'])
scraper = Scraper.Scraper()
scraper.get_balances_bitcoin_from_mempool(c.config_file['public_keys']['btc'])
scraper = Scraper.Scraper()
