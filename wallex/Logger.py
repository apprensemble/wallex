import time,os, json

class Logger:

  def __init__(self,history_file="hf.json"):
    # I need a temporary unik file for this information.
    self.lock_done = False
    history = {
    }
    try:
      history = self.load_file(history_file)
    except:
      self.save_to_file(history_file,history)

    self.history_file = history_file
    self.history = history

  def unlock(self):
    if self.lock_done:
      try:
        os.rmdir("lock_wallex")
        self.lock_done = False
      except FileNotFoundError:
        print("Le lock n'a pu etre trouvé!!! attention...")
    else:
      print("vous n'avez jamais effectué de lock..")

  def lock(self):
    stamp = time.time()+5
    newStamp = time.time()+0
    if self.lock_done:
      self.unlock()
    lock_done = False
    while stamp - newStamp > 0:
      try:
        os.mkdir("lock_wallex")
        lock_done = True
        newStamp = stamp
      except FileExistsError:
        newStamp = time.time()
        print("another instance running...")
        time.sleep(1)
    self.lock_done = lock_done
    return lock_done

  def load_file(self,filename):
    """
    open json file
    return an object
    """
    self.lock()
    if self.lock_done:
      if os.path.exists(filename):
        f = open(filename)
        fjson = json.loads(f.read())
        self.unlock()
        return fjson
      else:
        self.unlock()
        raise Exception("file does not exist...")
    else:
      raise Exception("A lock is already there...")

  def save_to_file(self,filename,data):
    """
    write dict to file

    filename,data: filename str,data dict
    return: None
    """
    self.lock()
    if self.lock_done:
      f = open(filename,'w')
      json.dump(data,f)
      self.unlock()
    else:
      raise Exception("A lock is already there...")

  def get_ref_time(self):
    #ref annee_jour de l'annee_heure et demi heure tel que
    # 24_242_15_2 : annee 24 JOUR 242 HEURE 15 apres 30 MN
    heure_presente = time.localtime()
    year = str(heure_presente.tm_year).split("20")[1]
    yday = str(heure_presente.tm_yday)
    if int(yday) < 10:
      yday = "00"+yday
    elif int(yday) < 100:
      yday = "0"+yday
    hour = str(heure_presente.tm_hour)
    if int(hour) < 10:
      hour = "0"+hour
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
    print("new recordt ",ref)