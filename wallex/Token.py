from typing import Any
import json


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



    def __init__(self,id, name, symbol, native_balance, type = "EVM") -> None:
        self.id = id
        self.name = name
        self.symbol = symbol
        self.native_balance = native_balance
        self.type = type
        self.missing_exchange_rate = True
    
    def __init__(self,id, name, symbol, native_balance, type, exchange_rate) -> None:
        self.id = id
        self.name = name
        self.symbol = symbol
        self.native_balance = native_balance
        self.exchange_rate = exchange_rate
        self.type = type
        self.usd_balance = exchange_rate * native_balance
        self.missing_exchange_rate = False

    def __init__(self,entry):
        self.id = entry['id']
        self.name = entry['name']
        self.symbol = entry['symbol']
        self.native_balance = entry['native_balance']
        if "exchange_rate" in entry.keys():
            self.exchange_rate = entry['exchange_rate']
            self.usd_balance = entry['exchange_rate'] * entry['native_balance']
            self.missing_exchange_rate = False
        else:
            self.missing_exchange_rate = True
        self.type = entry['type']
        self.blockchain = entry['blockchain']

    def add_exchange_rate(self,exchange_rate):
        self.usd_balance = float(self.native_balance) * float(exchange_rate)
        self.exchange_rate = float(exchange_rate)
        self.missing_exchange_rate = False

    def get_json_entry(self):
        return json.dumps(self.__dict__)

    def show_usd_price(self):
        try:
            print(self.symbol," ",self.usd_balance)
        except AttributeError as ae:
            print(self.symbol," pas de valeur usd")