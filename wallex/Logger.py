import time, json

class Logger:

  def __init__(self,history_file="hf.json"):
    history = {
    }
    try:
      history = self.load_file(history_file)
    except:
      self.save_to_file(history_file,history)

    self.history_file = history_file
    self.history = history

  def load_file(self,filename):
    """
    open json file
    return an object
    """
    f = open(filename)
    fjson = json.loads(f.read())
    return fjson

  def save_to_file(self,filename,data):
    """
    write dict to file

    filename,data: filename str,data dict
    return: None
    """
    f = open(filename,'w')
    json.dump(data,f)

  def get_ref_time(self):
    #ref annee_jour de l'annee_heure et demi heure tel que
    # 24_242_15_2 : annee 24 JOUR 242 HEURE 15 apres 30 MN
    heure_presente = time.localtime()
    year = str(heure_presente.tm_year).split("20")[1]
    yday = str(heure_presente.tm_yday)
    hour = str(heure_presente.tm_hour)
    minutes = heure_presente.tm_min
    if minutes > 30:
      demi_h = str(2)
    else:
      demi_h = str(1)
    return year+"_"+yday+"_"+hour+"_"+demi_h

    
  def add_content(self,content):
    ref = self.get_ref_time()
    if ref in self.history:
      self.history[ref].update(content)
    else:
      self.history.update({ref:content})
    self.save_to_file(self.history_file,self.history)
    print("new record")