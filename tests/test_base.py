from myblockscoutlib import base

def test_sum_tokens_usd_balances():
    entries = {
        '1': {
            'symbol': '1',
            'usd_balance': 10
        },
        '2': {
            'symbol': '2',
            'usd_balance': 15
        }
    }
    assert base.sum_tokens_usd_balances(entries) ==  25

def test_update_exhange_rate_to_entry():
    entry = {
        'native_balance': 0.022
    }
    assert base.update_exchange_rate_to_entry(entry,exhange_rate=2670)['usd_balance'] == 58.74 

 
    