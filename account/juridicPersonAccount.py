from .account import Account

class PjAccount(Account):

    def __init__(self, numberAccount, balance, cnpj, fantasyName, password):
        super().__init__(numberAccount, password, balance)
        self.cnpj = cnpj
        self.fantasyName = fantasyName