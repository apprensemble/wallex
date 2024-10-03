import json
from wallex import Cmc,Logger

# class de configuration myWalletLib

class Config:
    logger: Logger

    def __init__(self,config_file_name = "config_suivi_unitaire_real.json") -> None:
        f = open(config_file_name,"r")
        config_file = json.loads(f.read())
        self.logger = Logger.Logger()

        self.config_file = config_file
        self.wallex_common_data_dir = config_file['infos_globale']['wallex_common_data_dir']
        self.wallex_csv_dir = config_file['infos_globale']['wallex_csv_dir']
        self.wallex_config_dir = config_file['infos_globale']['wallex_config_dir']
        #mode test files
        self.wallex_common_data_dir_test = config_file['infos_globale']['wallex_common_data_dir_test']
        self.wallex_csv_dir_test = config_file['infos_globale']['wallex_csv_dir_test']
        self.wallex_config_dir_test = config_file['infos_globale']['wallex_config_dir_test']

        self.cmc_file = f"{self.wallex_common_data_dir}{config_file['infos_globale']['cmc_file']}"
        self.cmc_api_key = config_file['private_keys']['cmc_api_key']
        self.moralis_api_key = config_file['private_keys']['moralis_api_key']
        self.zerion_api_key = config_file['private_keys']['zerion_api_key']
        self.evm_wallets = config_file['public_keys']['evm']
        self.svm_wallets = config_file['public_keys']['svm']
        self.egld_wallets = config_file['public_keys']['egld']
        self.btc_wallets = config_file['public_keys']['btc']
        self.svm_main_symbols = config_file['infos_globale']['main_svm_symbols']
        self.evm_main_symbols = config_file['infos_globale']['main_evm_symbols']

        self.cmc = Cmc.Cmc(self.cmc_file,self.cmc_api_key)

    def load_file(self,filename):
        """
        open json file
        return an object
        """
        return self.logger.load_file(filename)

    def save_to_file(self,filename,data):
        """
        write dict to file

        filename,data: filename str,data dict
        return: None
        """
        self.logger.save_to_file(filename,data)
        return True

    def convert_pubkey_to_wallet_name(self,pubkey):
        names = {}
        names.update(self.evm_wallets)
        names.update(self.btc_wallets)
        names.update(self.svm_wallets)
        names.update(self.egld_wallets)
        for name in names:
            if pubkey == names[name]:
                return name