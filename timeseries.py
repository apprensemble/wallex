#!/home/grillon/Documents/Exercices/wallex/.venv/bin/python
from wallex import WalletManager, TimeSeriesManager
wm = WalletManager.WalletManager()
wm.fulfill_wallet_manager(True)
wm.update_all_my_wallets()
psol = wm.mes_wallets['custom_phantom_sol']
psol.remove_token_from_blockchain("ORCA","Solana")
wm.mes_wallets['custom_phantom_sol'] = psol
wm.remove_token_from_wallet_in_blockchain('BLOOM','custom_cwl','Base')
wm.remove_token_from_wallet_in_blockchain('BOMB','custom_cwl','Base')
wm.save_my_personal_wallets()
wm = WalletManager.WalletManager()
wm.import_custom_wallets_from_json_file("all_my_wallets.json")
wm.update_all_my_wallets()
wm.get_total_by_wallet(True)
ts = TimeSeriesManager.TimeSeriesManager()
ts.save_global_df()