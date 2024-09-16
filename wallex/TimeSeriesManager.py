from wallex import WalletManager,Logger,Config
import pandas as pd
import time

class TimeSeriesManager():

  def __init__(self):
    self.c = Config.Config()
    wallet_file = f"{self.c.wallex_common_data_dir}all_my_wallets.json"
    self.parsed_quotes = self.c.cmc.get_parsed_quotes()
    wm = WalletManager.WalletManager()
    wm.import_custom_wallets_from_json_file(wallet_file)
    self.wm = wm
  
  def get_apr_for_amount_in_given_time(self,apr:float,amount:float,step:str):
    '''
    return apr by step of time (year/month/week/day/hour)

    :param apr: annualized apr in pct
    :param amount: in dollar
    :param step: (yearly/monthly/weekly/daily/hourly)

    return apr for the given amount in given time

    '''
    echelle_de_temps = {'yearly':1,'monthly':12,'weekly':52,'daily':365,'hourly':365*24}
    duree = echelle_de_temps[step]
    get_step_apr = (amount / 100) * apr / duree
    return get_step_apr

  def get_examples_apr_for_token(self,apr):
    #100$ / 200$ / 1000$ / 2000$
    result = {}
    for step in ['yearly','monthly','weekly','daily','hourly']:
      result[step] = {}
      for amount in [100,200,1000,2000]:
        result[step].update({amount:round(self.get_apr_for_amount_in_given_time(apr,amount,step),2)})

    return result

  def get_dataset_from_strategie(self,strategie:str,tags_list=[]):
    # a titre d'exemple
  #  dataset = {
  #      "labels": [
  #          "Data 1",
  #          "Data 2",
  #          "Data 3",
  #          "Data 4",
  #          "Data 5",
  #          "Data 6",
  #          "Data 7",
  #          "Data 8",
  #      ],
  #      "datasets": [{"data": [14, 22, 36, 48, 60, 90, 28, 1]}],
  #  }
    wm = self.wm
    if strategie.lower() == "all":
      tokens = wm.get_global_summarized_tokens()
    elif strategie.lower() == "composition":
      tokens = wm.get_portfolio_composition_by_type()
    elif strategie.lower() == "flexible_tags":
      tokens = wm.get_flexible_tags(tags_list) 
    elif strategie.lower() == "by_wallet":
      tokens = wm.get_total_by_wallet()
    elif strategie.lower() == "non_suivis" or strategie.lower() == "non_suivi":
      tokens = wm.get_tokens_non_suivi()
    else:
      tokens = wm.get_tokens_by_strategie(strategie)
    labels = list(tokens.keys())
    datasets = [{"data":list(tokens.values())}]
    dataset = {"labels":labels,"datasets":datasets,}

    return dataset

  def get_dataframe_from_strategie(self,strategie:str):
    data = self.get_dataset_from_strategie(strategie)
    resultat = {"labels":data['labels'],"values":data['datasets'][0]['data']}
    return pd.DataFrame(resultat)

  def get_dataframe_by_blockchain(self):
    wm = self.wm
    res = wm.get_tokens_by_blockchain()
    dfp = {'bc':[],'token':[],'balance':[]}
    for bc in res:
      for token in res[bc]:
        dfp['bc'].append(bc)
        dfp['token'].append(token)
        dfp['balance'].append(res[bc][token])

    df = pd.DataFrame(dfp)
    return df

  def get_global_dataframe(self):
    wm = self.wm
    all_wallets = wm.mes_wallets
    dfp = {'wallet':[],'bc':[],'token':[],'usd_balance':[]}
    for wallet in all_wallets:
      blockchains = all_wallets[wallet].get_detailled_balance_by_blockchain()
      for bc in blockchains:
        for tokens in blockchains[bc]:
          for token in tokens:
            dfp['wallet'].append(wallet)
            dfp['bc'].append(bc)
            dfp['token'].append(token)
            dfp['usd_balance'].append(tokens[token])
    df = pd.DataFrame(dfp)
    return df

  def fill_dfp_for_token(self,check,token):
    famille = ['stablecoin','ETH','BTC','SOL']
    flexible_tags = self.get_dataset_from_strategie("flexible_tags")['labels']
    all_yield = flexible_tags
    all_yield.append('locked')
    dfp = {'famille':[],'strategie':[],'vision':[]}
    r = 'autre'
    for f in famille:
      if check(token,f):
        r = f
        break
      else:
        r = 'autre'
    dfp['famille'] = r

    r = 'libre'
    for m in all_yield:
      if check(token,m):
        r = m
        dfp['strategie'] = 'invested'
        break
    if check(token,'hold'):
      dfp['vision'] = 'hold'
    else:
      dfp['vision'] = 'trade'
    if r == 'libre':
      dfp['strategie'] = 'trade'

    return dfp

  def get_global_dataframe_with_tags(self)->pd.DataFrame:
    '''
    get a full dataframe with full informations:

    :param famille: stable/eth/btc/sol/autres 
    :param strategie: non_suivi/trade/invested/earning(usd+/JLP/GMX)
    :param vision: hold / trade
    :param type_placement: lp,lpc,locked,stacked,farmed,lend/libre
    :param position: BEEFY/AERODROME/ETC.

    :return: DataFrame
    '''
    wm = self.wm
    all_wallets = wm.mes_wallets
    dfp = {'wallet':[],'bc':[],'token':[],'usd_balance':[],'famille':[],'strategie':[],'protocol':[],'vision':[],'position':[]}
    check = lambda token,strategie: True if token in self.get_dataset_from_strategie(strategie)['labels'] else False
    for wallet in all_wallets:
      blockchains = all_wallets[wallet].get_detailled_tokens_infos_by_blockchain()
      for bc in blockchains:
        for tokens in blockchains[bc]:
          for token in tokens:
            dfp['wallet'].append(wallet)
            dfp['bc'].append(bc)
            dfp['token'].append(token)
            try:
              dfp['usd_balance'].append(tokens[token]['usd_balance'])
            except:
              dfp['usd_balance'].append(0)
            dfp['position'].append(tokens[token]['position'])
            dfp['protocol'].append(tokens[token]['protocol'])
            dfp['famille'].append(tokens[token]['famille'])
            dfp['strategie'].append(tokens[token]['strategie'])
            dfp['vision'].append(tokens[token]['vision'])
    for i in dfp:
      print(i,(len(dfp[i])))
    df = pd.DataFrame(dfp)
    return df

  def get_full_df(self):
    wm = self.wm
    all_wallets = wm.mes_wallets
    dfp = {'wallet':[],'bc':[],'token':[],'exchange_rate':[],'native_balance':[],'usd_balance':[],'famille':[],'strategie':[],'protocol':[],'vision':[],'position':[],'origine':[]}
    check = lambda token,strategie: True if token in self.get_dataset_from_strategie(strategie)['labels'] else False
    for wallet in all_wallets:
      blockchains = all_wallets[wallet].get_detailled_tokens_infos_by_blockchain()
      for bc in blockchains:
        for tokens in blockchains[bc]:
          for token in tokens:
            dfp['wallet'].append(wallet)
            dfp['bc'].append(bc)
            dfp['token'].append(token)
            dfp['native_balance'].append(tokens[token]['native_balance'])
            dfp['origine'].append(tokens[token]['origine'])
            if tokens[token]['missing_exchange_rate']:
              dfp['usd_balance'].append(0)
              dfp['exchange_rate'].append(0)
            else:
              dfp['usd_balance'].append(tokens[token]['usd_balance'])
              dfp['exchange_rate'].append(tokens[token]['exchange_rate'])
            dfp['position'].append(tokens[token]['position'])
            dfp['protocol'].append(tokens[token]['protocol'])
            dfp['famille'].append(tokens[token]['famille'])
            dfp['strategie'].append(tokens[token]['strategie'])
            dfp['vision'].append(tokens[token]['vision'])
    for i in dfp:
      print(i,(len(dfp[i])))
    df = pd.DataFrame(dfp)
    return df


  def create_daily_list_for_apy(self,apr,sommes,jours,box):
    #apr = lambda apr,sommes, jours: (jours * ts.get_apr_for_amount_in_given_time(apr,sommes,'daily'))+sommes
    #apy = lambda apr,sommes, jours: sommes if jours <=0 else apy(apr,sommes+(ts.get_apr_for_amount_in_given_time(apr,sommes,'daily')),jours-1)
    capr = self.get_apr_for_amount_in_given_time(apr,sommes,'daily')
    if jours <= 0:
      return box
    else:
      box.append(sommes)
      return self.create_daily_list_for_apy(apr,sommes+capr,jours-1,box)

  def create_monthly_list_for_apy(self,apr,sommes,months,box):
    #apr = lambda apr,sommes, month: (month * ts.get_apr_for_amount_in_given_time(apr,sommes,'montly'))+sommes
    #apy = lambda apr,sommes, month: sommes if month <=0 else apy(apr,sommes+(ts.get_apr_for_amount_in_given_time(apr,sommes,'montly')),month-1)
    capr = self.get_apr_for_amount_in_given_time(apr,sommes,'monthly')
    if months <= 0:
      return box
    else:
      box.append(sommes)
      return self.create_monthly_list_for_apy(apr,sommes+capr,months-1,box)

  def create_monthly_ts_for_apy(self,apr,sommes,months,name="Apy"):
    box = self.create_monthly_list_for_apy(apr,sommes,months,[])
    start_date = time.strftime("%m/%d/%Y",time.localtime())
    rng = pd.date_range(start_date, periods=months, freq="MS")
    ts = pd.Series(box,index=rng,name=name)
    return ts

  def create_daily_ts_for_apy(self,apr,sommes,days,name="Apy"):
    box = self.create_daily_list_for_apy(apr,sommes,days,[])
    start_date = time.strftime("%m/%d/%Y",time.localtime())
    rng = pd.date_range(start_date, periods=days, freq="D")
    ts = pd.Series(box,index=rng,name=name)
    return ts

  def calcul_pct_from_diff(self,avant,apres):
    #p = lambda avant,apres: str(apres/avant*100-100)+" %"
    return apres/avant*100-100

  def calcul_apr_from_diff(self,avant,apres,nbr_jours):
    #dapr = lambda avant,apres,nbj: 365/nbj * (apres/avant*100-100)
    return 365/nbr_jours * (apres/avant*100-100)

  def save_global_df(self):
    wallex_csv_dir = self.c.wallex_csv_dir
    heure_presente = time.localtime()
    year = str(heure_presente.tm_year).split("20")[1]
    month = str(heure_presente.tm_mon)
    if int(month) < 10:
      month = "0"+month
    mday = str(heure_presente.tm_mday)
    if int(mday) < 10:
      mday = "0"+mday
    hour = str(heure_presente.tm_hour)
    if int(hour) < 10:
      hour = "0"+hour
    filename = f"{wallex_csv_dir}wallex_full_df_{year}{month}{mday}{hour}.csv"
    df = self.get_full_df()
    df.to_csv(filename,index=False)
    df = self.get_global_dataframe_with_tags()
    filename = f"{wallex_csv_dir}wallex_usd_df_{year}{month}{mday}{hour}.csv"
    df.to_csv(filename,index=False)