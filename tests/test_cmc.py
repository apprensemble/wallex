from wallex import Cmc

cmc_file = "res_cmc.json"
f = open("api_key.txt")
api_key = f.read().strip("\n")
cmc = Cmc.Cmc(cmc_file,api_key)

def test_prepare():
    assert "96a5f" in api_key 

def test_cmc_init():
    assert cmc.CMC_FILE_NAME == "res_cmc.json"

def test_get_parsed_quotes():
    assert cmc.get_parsed_quotes()["ETH"]['id'] == 1027 
    resultat = 0
    quotes = cmc.get_parsed_quotes()
    for id in quotes.keys():
        if quotes[id]['symbol'] == "BTC":
            resultat += 1
    assert resultat == 1

def test_separate_doublons_simple():
    simple,doublons = cmc.separate_solo_and_doublons_quotes()
    assert len(simple) == cmc.nbr_simple
    