#!/home/grillon/Documents/Exercices/wallex/.venv/bin/python
import sys, getopt
from wallex import WalletManager, TimeSeriesManager
def help():
  print ('timeseries.py [-r] to refresh quotes')
  print ('timeseries.py [-s] to refresh sources')
  print ('timeseries.py [-t] to use test files')

def main(argv):
  refresh = False
  refresh_sources = False
  mode_test = False
  try:
    opts, args = getopt.getopt(argv,"hrst",["refresh"])
  except getopt.GetoptError:
    help()
    sys.exit(2)
  for opt, arg in opts:
    if opt == '-h':
      help()
      sys.exit()
    elif opt in ("-r", "--refresh"):
      print("refresh quotes...")
      refresh = True
    elif opt in ("-s", "--refresh-sources"):
      print("refresh sources...")
      refresh_sources = True
    elif opt in ("-t", "--mode_test"):
      print("mode test activated...")
      mode_test = True
  wm = WalletManager.WalletManager(mode_test=mode_test)
  wm.fulfill_wallet_manager(refresh,refresh_sources=refresh_sources)
  wm.get_total_by_wallet(True)
  ts = TimeSeriesManager.TimeSeriesManager()
  ts.save_global_df()
main(sys.argv[1:])
