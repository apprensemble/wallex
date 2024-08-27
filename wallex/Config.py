import json
from wallex import Cmc

# class de configuration myWalletLib

class Config:

    def __init__(self,config_file_name = "config_suivi_unitaire_real.json") -> None:
        f = open(config_file_name,"r")
        config_file = json.loads(f.read())

        self.config_file = config_file
        self.cmc_file = config_file['infos_globale']['cmc_file']
        self.cmc_api_key = config_file['private_keys']['cmc_api_key']
        self.moralis_api_key = config_file['private_keys']['moralis_api_key']
        self.evm_wallets = config_file['public_keys']['evm']
        self.svm_wallets = config_file['public_keys']['svm']
        self.svm_main_symbols = config_file['infos_globale']['main_svm_symbols']
        self.evm_main_symbols = config_file['infos_globale']['main_evm_symbols']

        self.cmc = Cmc.Cmc(self.cmc_file,self.cmc_api_key)

