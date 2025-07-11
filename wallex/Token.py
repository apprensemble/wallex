from typing import Any
import time


class Token:
# schema class base
# get native_info
# get token_info
# update exchange_rate
# get total_balance
## reflexion :
# type: EVM / SOLANA / BTC / EGLD / ETC.
# Object TOKEN -> type, native_balance, usd_balance, exchaange_rate, contract_addr, symbol, name

    id: str
    name: str
    symbol: str
    type: str
    native_balance: float
    usd_balance: float
    exchange_rate: float
    contract_address: str
    missing_exchange_rate: bool


# les surdefinition n'existent pas :-/
#    def __init__(self,id, name, symbol, native_balance, type = "EVM") -> None:
#        self.id = id
#        self.name = name
#        self.symbol = symbol
#        self.native_balance = native_balance
#        self.type = type
#        self.missing_exchange_rate = True
#    
#    def __init__(self,id, name, symbol, native_balance, type, exchange_rate) -> None:
#        self.id = id
#        self.name = name
#        self.symbol = symbol
#        self.native_balance = native_balance
#        self.exchange_rate = exchange_rate
#        self.type = type
#        self.usd_balance = exchange_rate * native_balance
#        self.missing_exchange_rate = False

    def __init__(self,entry):
        self.id = entry['id']
        self.name = entry['name']
        self.symbol = entry['symbol']
        self.native_balance = float(entry['native_balance'])
        try:
            self.exchange_rate = float(entry['exchange_rate'])
            self.usd_balance = self.exchange_rate * self.native_balance
            self.missing_exchange_rate = False
        except (ValueError,KeyError):
            self.missing_exchange_rate = True
        self.type = entry['type']
        self.blockchain = entry['blockchain']
        if 'protocol' in entry:
            self.protocol = entry['protocol']
        else:
            self.protocol = 'libre'
        if 'position' in entry:
            self.position = entry['position']
        else:
            self.position = 'wallet'
        if 'origine' in entry:
            self.origine = entry['origine']
        else:
            self.origine = "simple"
        if 'vision' in entry:
            self.vision = entry['vision']
        else:
            self.vision = "trade"
        if 'famille' in entry:
            self.famille = entry['famille']
        else:
            self.famille = "autre"
        if 'strategie' in entry:
            self.strategie = entry['strategie']
        else:
            self.strategie = "non_suivi"

        if not self.missing_exchange_rate:
            if 'ref_exchange_rate' in entry:
                self.ref_exchange_rate = entry['ref_exchange_rate']
            else:
                self.ref_exchange_rate = entry['exchange_rate']
        else:
            self.ref_exchange_rate = None
            self.ref_date_comparaison = None
        if 'ref_native_balance' in entry:
            self.ref_native_balance = entry['ref_native_balance']
        else:
            self.ref_native_balance = None
        if 'ref_date_comparaison' in entry:
            self.ref_date_comparaison = entry['ref_date_comparaison']
        else:
            self.ref_date_comparaison = time.time()



    def compute_usd_balance(self):
        try:
            exchange_rate = self.exchange_rate
            self.usd_balance = round(float(self.native_balance) * float(exchange_rate),2)
        except (AttributeError,ValueError):
            self.missing_exchange_rate = True
            self.usd_balance = 0
            self.exchange_rate = 0
            try:
                if not self.native_balance:
                    self.native_balance = 0
                    print("Missing native_balance")
            except:
                self.native_balance = 0
                print("Missing native_balance attr")
            print("Missing exchange rate")

    def sum_token_values(self,new_token):
        if self.id == new_token.id and self.blockchain == new_token.blockchain and self.position == new_token.position:
            self.native_balance += new_token.native_balance
        self.compute_usd_balance()

    def add_exchange_rate(self,exchange_rate):
        self.usd_balance = round(float(self.native_balance) * float(exchange_rate),2)
        self.exchange_rate = float(exchange_rate)
        self.missing_exchange_rate = False
        if not self.ref_exchange_rate:
            self.add_ref_values(self.native_balance,self.exchange_rate,time.time())

    def init_ref_exchange_rate(self):
        if not self.ref_exchange_rate:
            self.add_ref_values(self.native_balance,self.exchange_rate,time.time())


    def get_json_entry(self):
        return self.__dict__

    def show_usd_price(self):
        try:
            print(self.symbol," ",self.usd_balance)
        except AttributeError as ae:
            pass
    
    def is_same_position(self,token):
        if self.id == token.id and self.blockchain == token.blockchain and self.position == token.position:
            return True
        else:
            return False

    def add_ref_values(self,ref_native_balance,ref_exchange_rate,ref_date_comparaison):
        self.ref_exchange_rate = float(ref_exchange_rate)
        self.ref_date_comparaison = ref_date_comparaison
        self.ref_native_balance = float(ref_native_balance)

    def copy_ref_values(self,token):
        if token.ref_native_balance:
            self.add_ref_values(token.ref_native_balance,token.ref_exchange_rate,token.ref_date_comparaison)
        else:
            self.add_ref_values(token.native_balance,token.ref_exchange_rate,token.ref_date_comparaison)
        


        