#!/home/grillon/Documents/Exercices/wallex/.venv/bin/python
from wallex import WalletManager, TimeSeriesManager
wm = WalletManager.WalletManager()
wm.fulfill_wallet_manager(True)
wm.get_total_by_wallet(True)
ts = TimeSeriesManager.TimeSeriesManager()
ts.save_global_df()
