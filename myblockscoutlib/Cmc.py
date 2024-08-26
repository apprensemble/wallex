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

    def save_cmc_quotes_to_file(self):
        f = open(self.CMC_FILE_NAME,'w')
        json.dump(self.initial_response,f)


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
            'convert':'USD',
            'sort':"volume_24h"
        }
        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': self.X_CMC_PRO_API_KEY,
        }
        if regenerate:
            fjson = self.get_with_parameters(url,parameters,headers)
            self.initial_response = fjson
        else:
            fjson = self.load_cmc_quotes_from_file()
        return fjson

    def get_USD_quote_of_symbols_from_cmc(self,symbols,regenerate=True):
        url = 'https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest'
        parameters = {
            'symbol': symbols,
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
            if hasattr(d,"keys"):
                d = d
            else:
                d = quotes['data'][d][0]
            symbol = d['symbol']
            if symbol in parsed_quotes.keys():
                doublons = True
                occurences += parsed_quotes[symbol]['occurences']
            exchange_rate = float(d['quote']['USD']['price'])
            cid = d['name']+ symbol
            id = d['id']
            parsed_quotes[symbol] = {
            'symbol': symbol,
            'id': id,
            'cid': cid,
            'doublons': doublons,
            'occurences': occurences,
            'name': d['name'],
            'exchange_rate': exchange_rate
            }
        return parsed_quotes

    def get_parsed_quotes_of_symbols_from_cmc(self,symbols,regenerate=True):
        try:
            quotes = self.get_USD_quote_of_symbols_from_cmc(symbols)
            if quotes['status']['error_code'] > 0:
                raise BaseException("erreur recuperation quotes",quotes)
        except BaseException as be:
            print(be)
        self.quotes = self.parse_quotes_from_cmc(quotes)
        return self.quotes

    def get_parsed_quotes(self,regenerate=False):
        try:
            quotes = self.get_USD_quotes_from_cmc(regenerate)
            if quotes['status']['error_code'] > 0:
                raise BaseException("erreur recuperation quotes",quotes)
        except BaseException as be:
            print(be)
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