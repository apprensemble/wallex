from myblockscoutlib import Cmc, mantle
import json

cmc_file = "res_cmc.json"
f = open("api_key.txt")
api_key = f.read().strip("\n")
cmc = Cmc.Cmc(cmc_file,api_key)

f = open("config_suivi_unitaire_real.json","r")
fjson = json.loads(f.read())

wallet = fjson['public_keys']['evm']['CWL']

def test_prepare():
    assert "96a5f" in api_key 

def test_cmc_init():
    assert cmc.CMC_FILE_NAME == "res_cmc.json"

def test_update_eth_usd_balance():
    entry = mantle.get_native_balances_from_blockscout(wallet)
    simple,doublons = cmc.separate_solo_and_doublons_quotes()
    assert mantle.update_exchange_rate_to_entry(entry,simple['ETH']['exchange_rate'])['usd_balance'] == round(simple['ETH']['exchange_rate'] * entry['native_balance'],2)

def test_update_eth_usd_balance_from_simple_parsed_quotes():
    entry = mantle.get_native_balances_from_blockscout(wallet)
    simple,doublons = cmc.separate_solo_and_doublons_quotes()
    assert mantle.update_exchange_rate_via_parsed_quotes(entry,simple)['usd_balance'] == round(simple['ETH']['exchange_rate'] * entry['native_balance'],2)

def test_mybalance_check():
    entry = mantle.get_native_balances_from_blockscout(wallet)
    simple,doublons = cmc.separate_solo_and_doublons_quotes() 
    entry = mantle.update_exchange_rate_via_parsed_quotes(entry,simple)
    entries = mantle.get_token_balances_from_blockscout(wallet)
    entries['ETH'] = entry
    assert mantle.sum_tokens_usd_balances(entries) > 1

def test_add_entry_to_entries():
    entry = mantle.get_native_balances_from_blockscout(wallet)
    simple,doublons = cmc.separate_solo_and_doublons_quotes() 
    entry = mantle.update_exchange_rate_via_parsed_quotes(entry,simple)
    entries = mantle.get_token_balances_from_blockscout(wallet)
    assert "ETH" not in entries.keys()
    mantle.add_one_entry_to_entries(entry,entries)
    assert "ETH" in entries.keys()

