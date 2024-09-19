from wallex import Token
class Tokens:
    entries: dict
    balance_by_blockchain: dict
    total_balance: float
    name: str

    def __init__(self,name="aucun"):
        self.entries = {

        }
        self.name = name
        self.balance_by_blockchain = {}

    def add_entry_(self,token: Token.Token):
        try:
            self.entries[token.blockchain][token.id] = token
        except KeyError:
            self.entries[token.blockchain] = {}
            self.entries[token.blockchain][token.id] = token
        return self.entries

    def add_entry(self,token: Token.Token):
        try:
            if token.id not in self.entries[token.blockchain]:
                self.entries[token.blockchain][token.id] = token
            elif self.entries[token.blockchain][token.id].is_same_position(token):
                self.entries[token.blockchain][token.id].sum_token_values(token)
            else:
                raise Exception(f"{token} dans la meme blockchain mais pas de meme type")
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
                resultat[blockchain] = round(resultat[blockchain],2)
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
            if blockchain in self.entries and id in self.entries[blockchain]:
                new_entry_token = Token.Token(entry)
                self.entries[blockchain][id].sum_token_values(new_entry_token)
            else:
                self.entries[blockchain][id] = Token.Token(entry)
        except KeyError:
            self.entries[blockchain] = {}
            self.entries[blockchain][id] = Token.Token(entry)
        return self.entries

    def add_json_entries_from_multi_blockchain(self,entries):
        # Il faudrait check les entries
        for blockchain in entries:
            if 'symbol' in entries[blockchain]:
                # it's an entry
                self.add_json_entry(entries[blockchain])
            else:
                for entry in entries[blockchain]:
                    self.add_entry(Token.Token(entries[blockchain][entry]))

    def add_tokens(self,tokens):
        for token in tokens:
            self.add_entry(token)
    
    def call_add_exchange_rate(self,token:Token,parsed_quotes,index:str):
        try: 
            split_index = index.split("_")
            if len(split_index) == 2:
                erindex = split_index[1]
                token.add_exchange_rate(parsed_quotes[erindex]['exchange_rate'])
            else:
                token.add_exchange_rate(parsed_quotes[index]['exchange_rate'])
        except KeyError as k:
            token.compute_usd_balance()
            print(k,"is missing from cmc_parsed_quotes")
        return True

    def update_all_missing_exchange_rate_via_parsed_quotes(self,parsed_quotes):
    # il suffit d'avoir les quotes dans un dict tel que dict[symbol][exchange_rate]
        entries = self.entries
        for blockchain in entries.keys():
            for index in entries[blockchain]:
                if entries[blockchain][index].missing_exchange_rate:
                    self.call_add_exchange_rate(entries[blockchain][index],parsed_quotes,index)
        return entries

    def update_all_exchange_rate_via_parsed_quotes(self,parsed_quotes):
    # il suffit d'avoir les quotes dans un dict tel que dict[symbol][exchange_rate]
        entries = self.entries
        for blockchain in entries.keys():
            for index in entries[blockchain]:
                self.call_add_exchange_rate(entries[blockchain][index],parsed_quotes,index)
        return entries

    def remove_token_from_blockchain(self,symbol,blockchain):
        removed_symbol = ""
        #symbol = symbol.upper()
        try:
            if symbol in self.entries[blockchain].keys():
                removed_symbol = self.entries[blockchain].pop(symbol)
        except KeyError as ke:
            print(ke)
        return removed_symbol


    #separated by ,
    def remove_tokens_from_blockchain(self,symbols,blockchain):
        removed_symbols = {}
        for symbol in str.split(symbols,","):
            removed_symbols[symbol.upper()] = self.remove_token_from_blockchain(symbol,blockchain)
        return removed_symbols

    #separated by ,
    def remove_tokens_from_blockchains(self,symbols,blockchains):
        removed_symbols = {}
        for symbol in str.split(symbols,","):
            for blockchain in blockchains.split(","):
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

    def get_detailled_balance_by_blockchain(self):
        bc = {}
        for blockchain in self.entries:
            bc[blockchain] = []
            for token in self.entries[blockchain]:
                try:
                    bc[blockchain].append({token:self.entries[blockchain][token].usd_balance})
                except AttributeError:
                    continue
        return bc

    def get_detailled_tokens_infos_by_blockchain(self):
        bc = {}
        for blockchain in self.entries:
            bc[blockchain] = []
            for token in self.entries[blockchain]:
                try:
                    bc[blockchain].append({token:self.entries[blockchain][token].get_json_entry()})
                except AttributeError:
                    continue
        return bc

    def get_detailled_balance_by_token(self):
        tokens = {}
        for blockchain in self.entries:
            for token in self.entries[blockchain]:
                if token in tokens.keys():
                    if blockchain in tokens[token]:
                        tokens[token][blockchain] += self.entries[blockchain][token].usd_balance
                    else:
                        try:
                            tokens[token].update({blockchain:self.entries[blockchain][token].usd_balance})
                        except AttributeError:
                            continue
                else:
                    try:
                        tokens[token] = {blockchain:self.entries[blockchain][token].usd_balance}
                    except AttributeError:
                        continue
        return tokens

    def get_detailled_balance_by_summarized_token(self,ordo=True):
        tokens = {}
        for blockchain in self.entries:
            for token in self.entries[blockchain]:
                if token in tokens.keys():
                    try:
                        tokens[token] += round(self.entries[blockchain][token].usd_balance,2)
                    except AttributeError:
                        continue
                else:
                    try:
                        tokens[token] = round(self.entries[blockchain][token].usd_balance,2)
                    except AttributeError:
                        continue
        if sorted:
            resultat = dict(sorted(tokens.items(), key=lambda item: item[1],reverse=True))
        else:
            resultat = tokens
        return resultat

    def rename_token_in_blockchain(self,old_token_name,new_token_name,blockchain):
       if blockchain in self.entries:
            if old_token_name in self.entries[blockchain]:
                self.entries[blockchain][new_token_name] = self.entries[blockchain][old_token_name]
                self.remove_token_from_blockchain(old_token_name,blockchain)
                return True
       return False


    def change_symbol1_to_symbol2_on_blockchain_for_token_name(self,symbol1,symbol2,blockchain,token_name):
        if blockchain in self.entries:
            if symbol1 in self.entries[blockchain]:
                if token_name in self.entries[blockchain][symbol1].name:
                   self.entries[blockchain][symbol1].symbol = symbol2
                   self.entries[blockchain][symbol1].id = symbol2
                   self.rename_token_in_blockchain(symbol1,symbol2,blockchain)
                   return True
        return False

    def change_symbol1_to_symbol2_on_blockchain_for_complexe_token_name(self,symbol1,symbol2,blockchain,complexe_token_name):
        resultat = False
        tokens_to_rename = {}
        if blockchain in self.entries:
                for element in self.entries[blockchain].keys():
                    if symbol1 in element:
                        if complexe_token_name in element:
                            old_name = self.entries[blockchain][element].symbol
                            new_name = self.entries[blockchain][element].symbol.replace(f"_{symbol1}",f"_{symbol2}")
                            self.entries[blockchain][element].symbol = new_name
                            self.entries[blockchain][element].id = new_name
                            tokens_to_rename.update({old_name:new_name})
                            resultat = True
        if resultat == True:
            self.rename_token_in_blockchain(old_name,new_name,blockchain)
        return resultat
         