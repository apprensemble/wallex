from myblockscoutlib import Token,Wallet,base,Config

c = Config.Config()
mon_wallet = Wallet.Tokens()
parsed_quotes = c.cmc.get_parsed_quotes(False)
solana_entries = {'PYTH': 
                  {'id': 'PYTH', 'symbol': 'PYTH', 'name': 'Pyth Network', 'native_balance': '92046268', 'blockchain': 'Solana', 'type': 'SVM', 
                   'contract_address': '6Xk28XsA4FUVdydTEqcH51HxaMDzbTZZEi7AbKxLzj54'}, 
                'NFT': 
                   {'id': 'NFT', 'symbol': 'NFT', 'name': ' Mysterious Box', 'native_balance': '1', 'blockchain': 'Solana', 'type': 'SVM', 
                    'contract_address': '7mXnqYm4d3tyBNCEVbeKUj2yjf2kndPLTAtAYanduBpL'}, 
                'DOGGO': 
                    {'id': 'DOGGO', 'symbol': 'DOGGO', 'name': 'DOGGO', 'native_balance': '226426.69691', 'blockchain': 'Solana', 'type': 'SVM', 
                     'contract_address': '2YJSevxgvwruyWXb9kiuo66VRLTWyNDiJ3eaeiFT8kPC'},
                     }

sol_balance = {'id': 'SOL', 'symbol': 'SOL', 'name': 'Solana', 'native_balance': 0.281498155, 'blockchain': 'Solana', 'type': 'SVM'}

def test_add_json_entries():
    mon_wallet.add_json_entries(solana_entries)
    mon_wallet.update_all_missing_exchange_rate_via_parsed_quotes(parsed_quotes)
    mon_wallet.add_json_entry(sol_balance)
    assert mon_wallet.entries['SOL'].native_balance == sol_balance['native_balance']

def test_sum_total_balance():
    mon_wallet.add_json_entries(solana_entries)
    mon_wallet.update_all_missing_exchange_rate_via_parsed_quotes(parsed_quotes)
    mon_wallet.add_json_entry(sol_balance)
    mon_wallet.update_all_missing_exchange_rate_via_parsed_quotes(parsed_quotes)
    #mon_wallet.remove_token("pyth")
    removed_entries = mon_wallet.remove_tokens("pyth,sol")
    assert mon_wallet.sum_total_balance() < 1
    assert len(removed_entries.keys()) == 2

def test_add_missing_symbols():
    c.cmc.get_missing_main_symbols(c.svm_main_symbols)

