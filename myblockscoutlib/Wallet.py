from myblockscoutlib import Token
class Tokens:
    entries: dict
    balance_by_blockchain: dict
    total_balance: float

    def __init__(self):
        self.entries = {

        }
        self.balance_by_blockchain = {}

    def add_entry(self,token: Token):
        self.entries[token.id] = token
        return self.entries

    def sum_balance_by_blockchain(self):
        entries = self.entries
        resultat = {}
        for key in self.entries.keys():
            if entries[key].missing_exchange_rate:
                continue
            if not entries[key].blockchain in resultat:
                resultat[entries[key].blockchain] = 0.0
            resultat[entries[key].blockchain] += entries[key].usd_balance
        self.balance_by_blockchain = resultat
        return self.balance_by_blockchain

    def sum_total_balance(self):
        balances = self.sum_balance_by_blockchain()
        total = 0.0
        for key in balances:
            total += balances[key]
        self.total_balance = total
        return self.total_balance

    def add_json_entries(self,entries):
        for entry in entries:
            self.add_entry(Token.Token(entries[entry]))

    def add_json_entry(self,entry):
        self.entries[entry['id']] = Token.Token(entry)
        return self.entries

    def add_tokens(self,tokens):
        for token in tokens:
            self.add_entry(token)

    def update_all_missing_exchange_rate_via_parsed_quotes(self,parsed_quotes):
    # il suffit d'avoir les quotes dans un dict tel que dict[symbol][exchange_rate]
        entries = self.entries
        for index in entries.keys():
            if entries[index].missing_exchange_rate:
                try: 
                    entries[index].add_exchange_rate(parsed_quotes[index]['exchange_rate'])
                except KeyError as k:
                    print(k,"is missing from cmc_parsed_quotes")
        return entries

    def remove_token(self,symbol):
        removed_symbol = ""
        symbol = symbol.upper()
        if symbol in self.entries.keys():
            removed_symbol = self.entries.pop(symbol)
        return removed_symbol


    #separated by ,
    def remove_tokens(self,symbols):
        removed_symbols = {}
        for symbol in str.split(symbols,","):
            removed_symbols[symbol.upper()] = self.remove_token(symbol)
        return removed_symbols

    def list_tokens(self):
        for token in self.entries:
            print(self.entries[token].get_json_entry())

    def show_usd_prices(self):
        for token in self.entries:
            self.entries[token].show_usd_price()
        