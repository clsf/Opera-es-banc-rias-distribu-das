from .account import Account

class SharedAccount (Account):
    def __init__(self, accountNumber, balance, cpfs, names, password, bankName):
        super().__init__(accountNumber, balance, password, bankName)
        self.cpfs = cpfs
        self.names = names

    def getHoldersByCpf(self, cpf):
        finded_accounts = []
        if cpf in self.cpfs:
            finded_accounts.append(self)
        return finded_accounts
    
    def verifyHoldByCpf(self, cpf):
        return cpf in self.cpfs 
    

    def to_dict(self):
        return {
            "accountNumber": self.accountNumber,
            "balance": self.balance,
            "cpfs": self.cpfs,
            "holdBalance": self.holdBalance,
            "names": self.names,
            "password": self.password,
            "version": self.version,
            "bank_name": self.bankName,
            "type_account":'sh' 
        }
