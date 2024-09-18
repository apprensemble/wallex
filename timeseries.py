#!/home/grillon/Documents/Exercices/wallex/.venv/bin/python
import sys, getopt
from wallex import WalletManager, TimeSeriesManager
def help():
  print ('timeseries.py [-r] to refresh quotes')

def main(argv):
  refresh = False
  try:
    opts, args = getopt.getopt(argv,"hr",["refresh"])
  except getopt.GetoptError:
    help()
    sys.exit(2)
  for opt, arg in opts:
    if opt == '-h':
      help()
      sys.exit()
    elif opt in ("-r", "--refresh"):
      refresh = True
  wm = WalletManager.WalletManager()
  wm.fulfill_wallet_manager(refresh)
  wm.get_total_by_wallet(True)
  ts = TimeSeriesManager.TimeSeriesManager()
  ts.save_global_df()
main(sys.argv[1:])