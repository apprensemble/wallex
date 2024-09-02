from selenium import webdriver 
from selenium.webdriver import Chrome 
from selenium.webdriver.common.by import By 
import time
import json
from wallex import Logger

class Scraper:
  #attr driver
  #frequence en seconde

  def __init__(self,history_file="hf.json",frequence=1):
    # { {provider -> [times]},{...}}
    tl = {
      "debank": [0] 
    }
    self.tl = tl
    # Define the Chrome webdriver options
    options = webdriver.ChromeOptions() 
    options.add_argument("--headless") # Set the Chrome webdriver to run in headless mode for scalability

    # By default, Selenium waits for all resources to download before taking actions.
    # However, we don't need it as the page is populated with dynamically generated JavaScript code.
    options.page_load_strategy = "none"

    # Pass the defined options objects to initialize the web driver 
    driver = Chrome(options=options) 
    # Set an implicit wait of 5 seconds to allow time for elements to appear before throwing an exception
    driver.implicitly_wait(15)
    self.driver = driver
    # history file
    # { YEARYDAYH: {pubkey: [total]},{...}}
    history = Logger.Logger(history_file)
    self.history = history
    self.frequence = frequence

  def time_checker(self,provider):
    """
    Check the distance between two identical scape

    :param provider: website providing info(as debank)
    :param timelog_file: param optional file name tl.json)

    :return: True if more than frequence
    """
    present = int(time.time())
    elapsed_time = present - self.tl[provider][-1]
    self.tl[provider].append(present)
    return (elapsed_time) > self.frequence

  def get_balance_evm_from_debank(self,evm_pubkey):
    """
    get balance of evm_pubkey from debank by scraping

    :param evm_pubkey: hash de votre wallet evm
    :return: USD

    """
    #ref annee_jour de l'annee_heure tel que
    # 24_242_15 : annee 24 JOUR 242 HEURE 15
    if self.time_checker("debank"):
      url_dbank = "https://debank.com/profile/" 
      self.driver.get(url_dbank+evm_pubkey) 
      time.sleep(20)

      content = self.driver.find_element(By.CSS_SELECTOR, "div[class*='HeaderInfo_totalAssetInner__HyrdC HeaderInfo_curveEnable__HVRYq'")
      resultat = {evm_pubkey:round(float(content.text.replace("$","").replace(",","")),2)}
      self.history.add_content(resultat)
      return resultat[evm_pubkey]
    else:
      print("laissez le scraper souffler 30sec svp...")

  def get_balances_evm_from_debank(self,evm_wallets):
    resultat = {}
    for evm_wallet in evm_wallets.keys():
      resultat[evm_wallet] = round(float(self.get_balance_evm_from_debank(evm_wallets[evm_wallet])),2)
    return resultat

  def get_balance_bitcoin_from_mempool(self,btc_pubkey):
    url_mempool = "https://mempool.space/address/" 
    self.driver.get(url_mempool+btc_pubkey) 
    time.sleep(15)

    content = self.driver.find_element(By.CSS_SELECTOR, "span[class*='green-color'")
    resultat = {btc_pubkey:round(float(content.text.replace("$","").replace(",","")),2)}
    self.history.add_content(resultat)
    return resultat[btc_pubkey]

  def get_balances_bitcoin_from_mempool(self,btc_wallets):
    resultat = {}
    for btc_wallet in btc_wallets.keys():
      resultat[btc_wallet] = round(float(self.get_balance_bitcoin_from_mempool(btc_wallets[btc_wallet])),2)
    return resultat

      # egld / multivers / xPortal all the same 
  def get_balance_multivers_from_explorer(self,egld_pubkey):
    url_egld = "https://explorer.multiversx.com/accounts/"
    self.driver.get(url_egld+egld_pubkey) 
    time.sleep(15)

    content = self.driver.find_elements(By.CSS_SELECTOR, "span[class*='cursor-context text-truncate'")
    resultat = {egld_pubkey:round(float(content[2].text.replace("$","").replace(",","")),2)}
    self.history.add_content(resultat)
    return resultat[egld_pubkey]

  def get_balances_multivers_from_explorer(self,egld_wallets):
    resultat = {}
    for egld_wallet in egld_wallets.keys():
      resultat[egld_wallet] = round(float(self.get_balance_multivers_from_explorer(egld_wallets[egld_wallet])),2)
    return resultat

  def get_balance_solana_from_solscan(self,sol_pubkey):
    url_solscan = "https://solscan.io/account/"
    self.driver.get(url_solscan+sol_pubkey)
    time.sleep(15)

    content = self.driver.find_elements(By.CSS_SELECTOR,"div[class*='not-italic font-normal text-[14px] leading-[24px] text-neutral5'")
    resultat_1 = 0.0
    resultat_2 = 0.0
    try:
      resultat_1 = round(float(content[1].text.replace("($","").replace(",","").replace(")","")),2)
    except:
      resultat_1 = 0.0
    try:
      resultat_2 = round(float(content[3].text.replace("($","").replace(",","").replace(")","")),2)
    except:
      resultat_2 = 0.0
    resultat = {sol_pubkey:round(resultat_1+resultat_2,2)}
    self.history.add_content(resultat)
    return resultat[sol_pubkey]

  def get_balances_solana_from_solscan(self,sol_wallets):
    resultat = {}
    for sol_wallet in sol_wallets.keys():
      resultat[sol_wallet] = round(float(self.get_balance_solana_from_solscan(sol_wallets[sol_wallet])),2)
    return resultat

  def get_history(self):
    return self.history.history