from .account import Account

class PfAccount(Account):
    def __init__(self, accountNumber, balance, cpf, name, password, bankName):
        super().__init__(accountNumber, balance, password, bankName)
        self.cpf = cpf
        self.name = name 


    def to_dict(self):
        return {
            "accountNumber": self.accountNumber,
            "balance": self.balance,
            "cpf": self.cpf,
            "holdBalance": self.holdBalance,
            "name": self.name,
            "password": self.password,
            "version": self.version,
            "bank_name": self.bankName,
            "type_account":'pf' 
        }
