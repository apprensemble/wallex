from wallex import Token
class Tokens:
    entries: dict
    balance_by_blockchain: dict
    total_balance: float

    def __init__(self):
        self.entries = {

        }
        self.balance_by_blockchain = {}

    def add_entry(self,token: Token.Token):
        try:
            self.entries[token.blockchain][token.id] = token
        except KeyError:
            self.entries[token.blockchain] = {}
            self.entries[token.blockchain][token.id] = token
        return self.entries

    def sum_balance_by_blockchain(self):
        entries = self.entries
        resultat = {}
        for blockchain in self.entries.keys():
            for key in self.entries[blockchain]:
                if entries[blockchain][key].missing_exchange_rate:
                    continue
                if not blockchain in resultat:
                    resultat[blockchain] = 0.0
                resultat[blockchain] += entries[blockchain][key].usd_balance
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
        # Il faudrait check les entries
        if 'symbol' in entries:
            # it's an entry
            self.add_json_entry(entries)
        else:
            for entry in entries:
                self.add_entry(Token.Token(entries[entry]))

    def add_json_entry(self,entry):
        blockchain = entry['blockchain']
        id = entry['id']
        try:
            self.entries[blockchain][id] = Token.Token(entry)
        except KeyError:
            self.entries[blockchain] = {}
            self.entries[blockchain][id] = Token.Token(entry)
        return self.entries

    def add_tokens(self,tokens):
        for token in tokens:
            self.add_entry(token)

    def update_all_missing_exchange_rate_via_parsed_quotes(self,parsed_quotes):
    # il suffit d'avoir les quotes dans un dict tel que dict[symbol][exchange_rate]
        entries = self.entries
        for blockchain in entries.keys():
            for index in entries[blockchain]:
                if entries[blockchain][index].missing_exchange_rate:
                    try: 
                        entries[blockchain][index].add_exchange_rate(parsed_quotes[index]['exchange_rate'])
                    except KeyError as k:
                        print(k,"is missing from cmc_parsed_quotes")
        return entries

    def remove_token_from_blockchain(self,symbol,blockchain):
        removed_symbol = ""
        symbol = symbol.upper()
        if symbol in self.entries[blockchain].keys():
            removed_symbol = self.entries[blockchain].pop(symbol)
        return removed_symbol


    #separated by ,
    def remove_tokens_from_blockchain(self,symbols,blockchain):
        removed_symbols = {}
        for symbol in str.split(symbols,","):
            removed_symbols[symbol.upper()] = self.remove_token_from_blockchain(symbol,blockchain)
        return removed_symbols

    def list_tokens(self):
        for blockchain in self.entries:
            print(" ")
            print(blockchain)
            print(" ")
            for token in self.entries[blockchain]:
                print(self.entries[blockchain][token].get_json_entry())

    def show_usd_prices(self):
        for blockchain in self.entries:
            print(" ")
            print(blockchain)
            print(" ")
            for token in self.entries[blockchain]:
                self.entries[blockchain][token].show_usd_price()
        
    def show_tokens_without_exchange_rate(self):
        for blockchain in self.entries:
            print(" ")
            print(blockchain)
            print(" ")
            for token in self.entries[blockchain]:
                if self.entries[blockchain][token].missing_exchange_rate:
                    entry = self.entries[blockchain][token]
                    print(entry.id," ",entry.native_balance)
