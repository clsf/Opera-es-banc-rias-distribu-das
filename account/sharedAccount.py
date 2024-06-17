from .account import Account

class SharedAccount (Account):
    def __init__(self, accountNumber, balance, cpfs, names, password):
        super().__init__(accountNumber, balance, password)
        self.cpfs = cpfs
        self.names = names

    def getHoldersByCpf(self, cpf):
        finded_accounts = []
        if cpf in self.cpfs:
            finded_accounts.append(self)
        return finded_accounts
    
    def verifyHoldByCpf(self, cpf):
        return cpf in self.cpfs 