from wallex import Token,solana,Wallet,base,Config, optimism, arbitrum, mantle, zerion, WalletManager,TimeSeriesManager
from importlib import reload
from wallex.Config import Info

class AssistantDebug:

  def __init__(self):
    ts = TimeSeriesManager.TimeSeriesManager()
    #ts.get_full_df()
    df = ts.get_full_df_with_apr()
    self.ts = ts
    self.df = df
    self.li = lambda bc,wallet: {name:contenu for i in wallet.get_detailled_tokens_infos_by_blockchain()[bc] for name,contenu in i.items()}
    self.ddata = lambda data,info: {i:data[i][info.value] if info.value in data[i] else 0 for i in data}
    self.Info = Info
    self.parsed_quotes = ts.wm.parsed_quotes
    self.active_data = {'nom_wallet':'custom_cwl','bc':'Base','token':'ETH'}

  def define_active_data(self,nom_wallet,bc,token):
    self.active_data = {'nom_wallet':nom_wallet,'bc':bc,'token':token}
    return self.active_data

  def set_active_data(self,nom_wallet=None,bc=None,token=None):
    if nom_wallet:
      self.active_data['nom_wallet'] = nom_wallet
    if bc:
      self.active_data['bc'] = bc
    if token:
      self.active_data['token'] = token
    return list(self.active_data.values())

  def get_wallet(self,name_wallet=None):
    name_wallet,bc,token = self.set_active_data(name_wallet)
    return self.ts.wm.mes_wallets[name_wallet]

  def get_sum_by_wallet(self):
    return self.ts.wm.get_total_by_wallet()

  def get_sum_wallet_by_blockchain(self,name_wallet=None):
    name_wallet,bc,token = self.set_active_data(name_wallet)
    wallet: Wallet.Tokens = self.ts.wm.mes_wallets[name_wallet]
    return wallet.sum_balance_by_blockchain()

  def get_detailled_infos_from_wallet_and_bc(self,wallet,bc):
    return self.li(bc,wallet)

  def get_detailled_infos_from_wallet_and_bc_by_name(self,name_wallet=None,bc=None):
    name_wallet,bc,token = self.set_active_data(name_wallet,bc)
    wallet = self.get_wallet(name_wallet)
    return self.li(bc,wallet)

  def get_info_from_wallet_bc_info(self,wallet,bc,info: Info=Info.USD):
    return self.ddata(self.li(bc,wallet),info)

  def get_info_from_wallet_bc_info_by_name(self,name_wallet=None,bc=None,info: Info=Info.USD):
    name_wallet,bc,token = self.set_active_data(name_wallet,bc)
    wallet = self.get_wallet(name_wallet)
    return self.ddata(self.li(bc,wallet),info)

  def get_info_from_wallet_bc_info_criteria_by_name(self,name_wallet=None,bc=None,info=Info.USD,criteria=lambda x: x[1] and x[1] > 0):
    name_wallet,bc,token = self.set_active_data(name_wallet,bc)
    wallet = self.get_wallet(name_wallet)
    data = self.ddata(self.li(bc,wallet),info)
    rf = filter(criteria,data.items())
    return list(rf)

  def get_info_from_wallet_bc_info_criteria(self,wallet,bc,info=Info.USD,criteria=lambda x: x[1] and x[1] > 0):
    data = self.ddata(self.li(bc,wallet),info)
    rf = filter(criteria,data.items())
    return list(rf)

  def get_detailled_info_from_wallet_bc_token_by_name(self,name_wallet=None,bc=None,token=None):
    name_wallet,bc,token = self.set_active_data(name_wallet,bc,token)
    wallet = self.get_wallet(name_wallet)
    data = self.li(bc,wallet)
    return data[token]