from wallex import WalletManager,Logger,Config
import pandas as pd

class TimeSeriesManager():

  def __init__(self,filename="hf_forecast.json"):
    self.history = Logger.Logger(filename)
    c = Config.Config()
    self.parsed_quotes = c.cmc.get_parsed_quotes()
    from wallex import WalletManager
    wm = WalletManager.WalletManager()
    wm.import_custom_wallets_from_json_file("all_my_wallets.json")
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

  def get_dataset_from_strategie(self,strategie:str):
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
    elif strategie.lower() == "flexible_yield":
      tokens = wm.get_flexible_yield() 
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

  def get_global_dataframe_with_tags(self)->pd.DataFrame:
    '''
    get a full dataframe with full informations:

    :param famille: stable/eth/btc/sol/autres 
    :param strategie: hold/non_suivi/trade
    :param placement: nom_defi ou libre
    :mode: lp,lpc,locked,stacked,farmed,lend

    :return: DataFrame
    '''
    wm = self.wm
    all_wallets = wm.mes_wallets
    dfp = {'wallet':[],'bc':[],'token':[],'usd_balance':[],'famille':[],'strategie':[],'placement':[],'mode_de_placement':[]}
    famille = ['stablecoin','ETH','BTC','SOL']
    flexible_yield = self.get_dataset_from_strategie("flexible_yield")['labels']
    check = lambda token,strategie: True if token in self.get_dataset_from_strategie(strategie)['labels'] else False
    for wallet in all_wallets:
      blockchains = all_wallets[wallet].get_detailled_balance_by_blockchain()
      for bc in blockchains:
        for tokens in blockchains[bc]:
          for token in tokens:
            dfp['wallet'].append(wallet)
            dfp['bc'].append(bc)
            dfp['token'].append(token)
            dfp['usd_balance'].append(tokens[token])
            if check(token,'non_suivi'):
              dfp['famille'].append('autre')
              dfp['strategie'].append('non_suivi')
              dfp['placement'].append('libre')
              dfp['mode_de_placement'].append('')
            else:
              r = 'libre'
              for m in flexible_yield:
                if check(token,m):
                  r = m
                  break
                else:
                  r = 'libre'
              dfp['mode_de_placement'].append(r)
              r = 'autre'
              for f in famille:
                if check(token,f):
                  r = f
                  break
                else:
                  r = 'autre'
              dfp['famille'].append(r)
              if check(token,'hold'):
                dfp['strategie'].append("hold")
              else:
                dfp['strategie'].append('trade')
              if len(token.split('_')) > 1:
                dfp['placement'].append(token.split('_')[0])
              else:
                dfp['placement'].append('libre')
    for i in dfp:
      print(i,(len(dfp[i])))
    df = pd.DataFrame(dfp)
    return df