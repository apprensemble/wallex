from myblockscoutlib import Cmc

cmc_file = "res_cmc.json"
f = open("api_key.txt")
api_key = f.read().strip("\n")
cmc = Cmc.Cmc(cmc_file,api_key)

def test_prepare():
    assert "96a5f" in api_key 

def test_cmc_init():
    assert cmc.CMC_FILE_NAME == "res_cmc.json"

def test_get_parsed_quotes():
    assert cmc.get_parsed_quotes()['EthereumETH']['id'] == 1027
    resultat = 0
    for key in cmc.get_parsed_quotes().keys():
        if "AERO" in key:
           resultat += 1 
    assert resultat > 0