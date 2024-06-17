from .account import Account

class PfAccount(Account):
    def __init__(self, accountNumber, balance, cpf, name, password):
        super().__init__(accountNumber, balance, password)
        self.cpf = cpf
        self.name = name 
