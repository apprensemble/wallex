from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import time
import json

class Cmc:
    def __init__(self,cmc_file_name,x_cmc_pro_api_key):
        self.CMC_FILE_NAME = cmc_file_name
        self.X_CMC_PRO_API_KEY = x_cmc_pro_api_key
        self.quotes = {}

    def load_cmc_quotes_from_file(self):
        f = open(self.CMC_FILE_NAME)
        fjson = json.loads(f.read())
        return fjson

    def load_cmc_quotes_from_arg_file(self,filename):
        f = open(filename)
        fjson = json.loads(f.read())
        return fjson

    def save_cmc_quotes_to_file(self):
        f = open(self.CMC_FILE_NAME,'w')
        json.dump(self.initial_response,f)

    def save_cmc_quotes_to_arg_file(self,filename):
        f = open(filename,'w')
        json.dump(self.initial_custom_response,f)

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
            self.save_cmc_quotes_to_file()
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
            self.initial_custom_response = fjson
        else:
            fjson = self.load_cmc_quotes_from_file()
        return fjson

    def parse_quotes_from_cmc(self,quotes):
        parsed_quotes = {}
        parsed_quotes['last_update'] = time.mktime(time.strptime(quotes['status']['timestamp'].split(".")[0],"%Y-%m-%dT%H:%M:%S"))
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
                parsed_quotes[symbol]['occurences'] = occurences
                parsed_quotes[symbol]['doublons'] = True
                symbol = symbol+str(occurences)
            try:
                exchange_rate = float(d['quote']['USD']['price'])
            except TypeError as te:
                print("acun taux d'echange pour", symbol)
                print(te)
                continue
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
                raise BaseException("erreur recuperation quotes",quotes,symbols)
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
            return self.quotes
        self.quotes = self.parse_quotes_from_cmc(quotes)
        return self.quotes

    def separate_solo_and_doublons_quotes(self,regenerate=False):
        doublons = {}
        simple = {}
        ndoublons = 0
        nsimple = 0
        quotes = self.get_parsed_quotes(regenerate)
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

    def get_missing_main_symbols(self,main_symbols,regenerate=True,filename="missing_symbols.json"):
        resultat = {}
        if not regenerate:
            resultat = self.load_cmc_quotes_from_arg_file(filename)
            return resultat
        missing = []
        for s in main_symbols.split(","):
            if s not in self.quotes.keys():
                missing.append(s)
        missing_symbols_string = ",".join(missing)
        if len(missing_symbols_string) > 0:
            resultat = self.get_parsed_quotes_of_symbols_from_cmc(missing_symbols_string)
        if len(resultat) > 0 and regenerate:
            self.save_cmc_quotes_to_arg_file(filename)
        return resultat

