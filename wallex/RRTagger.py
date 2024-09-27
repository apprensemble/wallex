from wallex import Config

class RR:
  def __init__(self,capital=1000,pct_max_loss=5,rrtags_filename=None,capital_filename=None,config=None,parsed_quote=None):
    if type(config) is Config.Config:
      self.c = config
    else:
      self.c = Config.Config()
    self.parsed_quotes = self.c.cmc.get_parsed_quotes()
    self.capital = {}
    if not rrtags_filename:
      rrtags_filename = f"{self.c.wallex_common_data_dir}RR.json"
      self.rrtags_filename = rrtags_filename
    if not capital_filename:
      capital_filename = f"{self.c.wallex_common_data_dir}capital.json"
    try:
      self.rrtags = self.c.load_file(rrtags_filename)
    except:
      self.rrtags = {}
    try:
      self.capital = self.c.load_file(capital_filename)
      if 'default' not in self.capital:
        raise Exception("init capital")
    except:
      ppmax = pct_max_loss
      pmax = round(capital * pct_max_loss / 100,2)
      self.capital.update({'default':{'capital':capital,'ppmax':ppmax,'pmax':pmax}})
      self.capital.update({'last_update':{'capital':capital,'ppmax':ppmax,'pmax':pmax,'famille':'default'}})
    self.capital_filename = capital_filename

  def get_capital(self,famille=None,arg=None):
    if famille == 'lst':
      return self.capital.keys()
    elif famille == 'all':
      return self.capital
    elif not famille:
      famille = 'last_update'
    elif famille not in self.capital.keys() and famille in self.capital['last_update']:
      arg = famille
      famille = 'last_update'
    else:
      famille = 'last_update'

    if arg in self.capital[famille]:
      return self.capital['last_update'][arg]
    else:
      return self.capital[famille]


  def save_rr(self):
    self.c.save_to_file(self.rrtags_filename,self.rrtags)
    self.c.save_to_file(self.capital_filename,self.capital)

  def set_capital(self,pct_loss,capital,famille=None):
    if not famille:
      famille = self.capital['last_update']['famille']
    pmax = round(capital * pct_loss / 100,2)
    self.capital.update({famille:{'capital':capital,'ppmax':pct_loss,'pmax':pmax}})
    self.capital.update({'last_update':{'capital':capital,'ppmax':pct_loss,'pmax':pmax,'famille':famille}})

  def check_price(self,token):
    if token in self.parsed_quotes:
      return self.parsed_quotes[token]['exchange_rate']
    else:
      return False

  def check_ref_price(self,token,df):
    if df[df['token'] == token]['ref_exchange_rate'].any():
      return df[df['token'] == token]['ref_exchange_rate'].mean()
    else:
      return False
      
  def check_ref_investissement(self,token,df):
    if df[df['token'] == token]['usd_balance'].any():
      return df[df['token'] == token]['usd_balance'].sum()
    else:
      return False
      
  def calcul_rr(self,prix,tp,sl):
    return round((tp-prix)/(prix-sl),2)

  def calcul_rr_with_autoprice(self,token,tp,sl):
    prix = self.check_price(token)
    if not prix:
      return False
    return self.calcul_rr(prix,tp,sl)

  def calcul_taille_position(self,prix,sl,coef=1):
    pmax = self.get_capital('pmax')
    return (pmax/(prix - sl)) * coef

  def calcul_gains_potentiels(self,prix,tp,taille_position):
    return round((tp - prix) * taille_position,2)

  def calcul_pertes_potentielles(self,prix,sl,taille_position):
    return round((prix - sl) * taille_position,2)

  def calcul_investissement(self,taille_position,prix):
    return round(taille_position * prix,2)

  def simulation_rr(self,token,tp,sl,prix=None,investissement=None,save_rr=False):
    if not prix:
      prix = self.check_price(token)
    if not prix:
      return False
    rr = self.calcul_rr(prix,tp,sl)
    if investissement:
      taille_position = investissement / prix
    else: 
      taille_position = self.calcul_taille_position(prix,sl)
    gainEst = self.calcul_gains_potentiels(prix,tp,taille_position)
    perteEst = self.calcul_pertes_potentielles(prix,sl,taille_position)
    if not investissement:
      investissement = self.calcul_investissement(taille_position,prix)
    pmax = self.get_capital('pmax')
    ppmax = self.get_capital('ppmax')
    simulation = {token:{'ref_price':prix,'tp':tp,'sl':sl,'pmax':pmax,'ppmax':ppmax,'taille_position':taille_position,'investissement':investissement,'rr':rr,'gainEst':gainEst,'perteEst':perteEst}}
    if save_rr:
      self.rrtags.update(simulation)
    return simulation
    
  def load_simulation_rr(self,token):
    if token in self.rrtags.keys():
      return self.rrtags[token]
    else:
      return {'ref_price': 0, 'tp': 0, 'sl': 0, 'pmax': 0.0, 'ppmax': 0, 'taille_position': 0.0, 'investissement': 0.0, 'rr': -1.0, 'gainEst': -0.0, 'perteEst': 0.0}

  def calcul_actual_rr(self,token,tp,sl,df,prix=None,investissement=None,save_rr=False):
    if not prix:
      prix = self.check_ref_price(token,df)
    if not prix:
      return False
    rr = self.calcul_rr(prix,tp,sl)
    if not investissement:
      investissement = self.check_ref_investissement(token,df)
    if investissement:
      taille_position = investissement / prix
    else: 
      taille_position = self.calcul_taille_position(prix,sl)
    gainEst = self.calcul_gains_potentiels(prix,tp,taille_position)
    perteEst = self.calcul_pertes_potentielles(prix,sl,taille_position)
    if not investissement:
      investissement = self.calcul_investissement(taille_position,prix)
    pmax = self.get_capital('pmax')
    ppmax = self.get_capital('ppmax')
    simulation = {token:{'ref_price':prix,'tp':tp,'sl':sl,'pmax':pmax,'ppmax':ppmax,'taille_position':taille_position,'investissement':investissement,'rr':rr,'gainEst':gainEst,'perteEst':perteEst}}
    if save_rr:
      self.rrtags.update(simulation)
    return simulation
