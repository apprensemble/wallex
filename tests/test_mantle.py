from wallex import Token,Wallet,mantle,Config

c = Config.Config()
mon_wallet = Wallet.Tokens()
parsed_quotes = c.cmc.get_parsed_quotes(False)
cwl_entries = {'USD+': 
               {'id': 'USD+', 'name': 'USD+', 'symbol': 'USD+',
                'contract_address': '0xB79DD08EA68A908A97220C76d19A6aA9cBDE4376', 'native_balance': 368.84610599999996,
                'usd_balance': 369.583798212, 'blockchain': 'Mantle', 'type': 'EVM', 'exchange_rate': 1.002},
                'bsdETH': 
                {'id': 'bsdETH', 'name': 'Based ETH', 'symbol': 'bsdETH', 'contract_address': '0xCb327b99fF831bF8223cCEd12B1338FF3aA322Ff',
                           'native_balance': 0.10032327921224769, 'usd_balance': 280.51793393653423, 
                           'blockchain': 'Mantle', 'type': 'EVM', 'exchange_rate': 2796.14}
                }
mantle_eth_balance = {'id': 'MNT', 'symbol': 'MNT', 'name': 'Mantle', 'native_balance': 0.23859492544325733, 'blockchain': 'Mantle', 'type': 'EVM'}

def add_json_entries():
    mon_wallet.add_json_entries(cwl_entries)
    assert mon_wallet.entries['USD+']['usd_balance'] == cwl_entries['USD+']
    mon_wallet.add_json_entry(mantle_eth_balance)
    assert mon_wallet.entries['MNT']['native_balance'] == mantle_eth_balance['native_balance']

def test_get_native_balance_from_blockscout():
    mantle_eth_balance = mantle.get_native_balance_from_blockscout(c.evm_wallets['CWL'])
    assert mantle_eth_balance['id'] == 'MNT'

def test_sum_tokens_usd_balances():
    mon_wallet.add_json_entries(cwl_entries)
    assert mon_wallet.sum_balance_by_blockchain()['Mantle'] == cwl_entries['USD+']['usd_balance'] + cwl_entries['bsdETH']['usd_balance']
    mon_wallet.add_json_entry(mantle_eth_balance)
    mantle_eth_balance2 = mon_wallet.update_all_missing_exchange_rate_via_parsed_quotes(parsed_quotes)
    assert mon_wallet.sum_balance_by_blockchain()['Mantle'] == cwl_entries['USD+']['usd_balance'] + cwl_entries['bsdETH']['usd_balance'] + mantle_eth_balance2['Mantle']['MNT'].usd_balance
    assert mon_wallet.sum_total_balance() == mon_wallet.sum_balance_by_blockchain()['Mantle']