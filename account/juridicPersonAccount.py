from .account import Account

class PjAccount(Account):

    def __init__(self, numberAccount, balance, cnpj, fantasyName, password, bankName):
        super().__init__(numberAccount, password, balance, bankName)
        self.cnpj = cnpj
        self.fantasyName = fantasyName

    def to_dict(self):
        return {
            "accountNumber": self.accountNumber,
            "balance": self.balance,
            "cnpj": self.cnpj,
            "holdBalance": self.holdBalance,
            "names": self.fantasyName,
            "password": self.password,
            "version": self.version,
            "bank_name": self.bankName,
            "type_account":'pj' 
        }