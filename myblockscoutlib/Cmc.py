from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json

class Cmc:
    def __init__(self,cmc_file_name,x_cmc_pro_api_key):
        self.CMC_FILE_NAME = cmc_file_name
        self.X_CMC_PRO_API_KEY = x_cmc_pro_api_key

    def load_cmc_quotes_from_file(self):
        f = open(self.CMC_FILE_NAME)
        fjson = json.loads(f.read())
        return fjson

    def get_with_parameters(self,url,parameters,headers):

        session = Session()
        session.headers.update(headers)

        try:
            response = session.get(url, params=parameters)
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            print(e)
        return response.json()

    def get_USD_quotes_from_cmc(self,regenerate=False):
        url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
        parameters = {
            'start':'1',
            'limit':'5000',
            'convert':'USD'
        }
        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': self.X_CMC_PRO_API_KEY,
        }
        if regenerate:
            fjson = self.get_with_parameters(url,parameters,headers)
        else:
            fjson = self.load_cmc_quotes_from_file()
        return fjson

    def parse_quotes_from_cmc(self,quotes):
        parsed_quotes = {}
        for d in quotes['data']:
            doublons = False
            occurences = 1
            symbol = d['symbol']
            if symbol in parsed_quotes.keys():
                doublons = True
                occurences += parsed_quotes[symbol]['occurences']
            cid = d['name']+ symbol
            id = d['id']
            parsed_quotes[symbol] = {
            'symbol': symbol,
            'id': id,
            'cid': cid,
            'doublons': doublons,
            'occurences': occurences,
            'name': d['name'],
            'exchange_rate': float(d['quote']['USD']['price'])
            }
        return parsed_quotes

    def get_parsed_quotes(self,regenerate=False):
        quotes = self.get_USD_quotes_from_cmc(regenerate)
        self.quotes = self.parse_quotes_from_cmc(quotes)
        return self.quotes

    def separate_solo_and_doublons_quotes(self):
        doublons = {}
        simple = {}
        ndoublons = 0
        nsimple = 0
        quotes = self.get_parsed_quotes()
        for id in quotes.keys():
            if quotes[id]['occurences'] > 1:
                doublons[id] = quotes[id]
                ndoublons += 1
            else:
                simple[id] = quotes[id]
                nsimple += 1
        self.simple = simple
        self.doublons = doublons
        self.nbr_simple = nsimple
        self.nbr_doublons = doublons
        print("nbr doublons: ",ndoublons,", nbr simple: ",nsimple)
        return simple,doublons
