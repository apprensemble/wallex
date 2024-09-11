from wallex import WalletManager,Logger,Config

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
    elif strategie.lower() == "non_suivis":
      tokens = wm.get_tokens_non_suivi()
    else:
      tokens = wm.get_tokens_by_strategie(strategie)
    labels = list(tokens.keys())
    datasets = [{"data":list(tokens.values())}]
    dataset = {"labels":labels,"datasets":datasets,}

    return dataset

  def get_complexe_dataset(self,strategie="by_blockchain"):
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
    res = wm.get_tokens_by_blockchain()
    labels_liste_bc = list(res.keys())
    values_liste_bc = []
    labels_details = {}
    values_details = {}
    for bc in labels_liste_bc:
      values_liste_bc.extend(res[bc].values())
      labels_details[bc] = list(res[bc].keys())
      values_details[bc] = list(res[bc].values())

    dataset = {
    "labels": labels_liste_bc.extend(labels_details),
    "datasets": [{"data": values_liste_bc,"label":"blockchain"},{"data":values_details['Solana'],"label":"Solana"},{"data":values_details['Base'],"label":"Base"}],
    }
    return dataset

    
    

