from wallex import Token,Wallet,arbitrum,Config

c = Config.Config()
mon_wallet = Wallet.Tokens()
parsed_quotes = c.cmc.get_parsed_quotes(False)
#blockchain cible
bc = "arbitrum".capitalize()
#données type blockscout
arbitrum_get_tokens = [
{
"token": {
    "address": "0xB79DD08EA68A908A97220C76d19A6aA9cBDE4376",
    "circulating_market_cap": "0.0",
    "decimals": "6",
    "exchange_rate": "1.0",
    "holders": "54850",
    "icon_url": "https://assets.coingecko.com/coins/images/39624/small/USD_.png?1723179227",
    "name": "USD+",
    "symbol": "USD+",
    "total_supply": "51953471558618",
    "type": "ERC-20",
    "volume_24h": "28436045.314446677"
},
"token_id": '',
"token_instance": '',
"value": "432036220"
},
{
"token": {
    "address": "0xCb327b99fF831bF8223cCEd12B1338FF3aA322Ff",
    "circulating_market_cap": "0.0",
    "decimals": "18",
    "exchange_rate": "2316.79",
    "holders": "1023",
    "icon_url": "https://assets.coingecko.com/coins/images/35774/small/Icon_White_on_Blue.png?1709793654",
    "name": "Based ETH",
    "symbol": "bsdETH",
    "total_supply": "2929507667109544350527",
    "type": "ERC-20",
    "volume_24h": "96451.56743665988"
},
"token_id": '',
"token_instance": '',
"value": "100323279212247688"
}]
arbitrum_get_native = {"message": "OK", "result": "76269589638401015", "status": "1"}

def test_get_native_balance_from_blockscout():
    arbitrum_native_balance = arbitrum.parse_native_response_from_blockscout(arbitrum_get_native)
    assert arbitrum_native_balance['id'] == 'ETH'

def test_get_tokens_balance_from_blockscout():
    cwl_entries = arbitrum.parse_response_from_blockscout(arbitrum_get_tokens)
    print(cwl_entries)
    assert cwl_entries['USD+']['usd_balance'] == 432.04

def add_json_entries():
    cwl_entries = arbitrum.parse_response_from_blockscout(arbitrum_get_tokens)
    arbitrum_eth_balance = arbitrum.parse_native_response_from_blockscout(arbitrum_get_native)
    mon_wallet.add_json_entries(cwl_entries)
    assert mon_wallet.entries['USD+']['usd_balance'] == cwl_entries['USD+']
    mon_wallet.add_json_entry(arbitrum_eth_balance)
    assert mon_wallet.entries['ETH']['native_balance'] == arbitrum_eth_balance['native_balance']

def test_sum_tokens_usd_balances():
    cwl_entries = arbitrum.parse_response_from_blockscout(arbitrum_get_tokens)
    arbitrum_eth_balance = arbitrum.parse_native_response_from_blockscout(arbitrum_get_native)
    mon_wallet.add_json_entries(cwl_entries)
    assert mon_wallet.sum_balance_by_blockchain()[bc] == cwl_entries['USD+']['usd_balance'] + cwl_entries['bsdETH']['usd_balance']
    mon_wallet.add_json_entry(arbitrum_eth_balance)
    arbitrum_native_balance2 = mon_wallet.update_all_missing_exchange_rate_via_parsed_quotes(parsed_quotes)
    assert mon_wallet.sum_balance_by_blockchain()[bc] == cwl_entries['USD+']['usd_balance'] + cwl_entries['bsdETH']['usd_balance'] + arbitrum_native_balance2[bc]['ETH'].usd_balance
    assert mon_wallet.sum_total_balance() == mon_wallet.sum_balance_by_blockchain()[bc]