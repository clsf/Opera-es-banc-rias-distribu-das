from account.fisicPersonAccount import PfAccount
from  account.juridicPersonAccount import PjAccount
from account.sharedAccount import SharedAccount

class Bank:

    


    def __init__(self, name):
        self.name = name
        self.accounts = {}
        self.numberAccount = 0;


    def registerPjAccount(self, cnpj, fantasyName, password):
        self.numberAccount += 1
        account = PjAccount(self.numberAccount, 0, cnpj, fantasyName, password)
        self.accounts[self.numberAccount] = account
        return account

    def registerPfAccount(self, cpf, name, passowrd):
        for account in self.accounts.values():
            if isinstance(account, PfAccount) and account.cpf == cpf:
                return None
        self.numberAccount += 1
        account = PfAccount(self.numberAccount, 0, cpf, name, passowrd)
        self.accounts[self.numberAccount] = account
        return account

    
    def registerSharedAccount(self, cpfs, names, password):
        self.numberAccount +=1
        account = SharedAccount(self.numberAccount, 0, cpfs, names, password)
        self.accounts[self.numberAccount] = account
        return account



    def getAccountByCpf(self, cpf):
        accountsFinded = []
        for account in self.accounts.values():
            if isinstance(account, PfAccount) and account.cpf==cpf:
                accountsFinded.append(account)
            
            elif isinstance(account, SharedAccount) and account.verifyHoldByCpf(cpf):
                accountsFinded.append(account)
        return accountsFinded

    def getAccountByCnpj(self, cnpj):
        accountsFinded = []
        for account in self.accounts.values():
            if isinstance(account, PjAccount) and account.cnpj == cnpj:
                accountsFinded.append(account)
        return accountsFinded
    
    def prepareTransfer(self, account, amount, transaction_timestamp):
        if account in self.accounts:
            account = self.accounts[account]
            if account.balance >= amount:
                if transaction_timestamp >= account.version:
                    account.holdBalance += amount
                    account.balance -= amount
                    account.version = transaction_timestamp 
                    return "prepared"
                else:
                    return "conflited"
            else:
                return "insufficient_funds"
        return "Account not found"
    

    def transfer(self, account, amount):
        if account in self.accounts:
            account = self.accounts[account]
            if account.holdBalance < amount:
                return "insufficient_funds"

            account.holdBalance -= amount
            return "ok"
        return "Account not found"


    def deposite(self, account, amount):
        account = self.accounts[account]
        if account != None:            
            account.balance+= amount
            return "deposit"
        else: 
            return "Account not found"
        
    def rollback(self, account, amount):
        if account in self.accounts:
            account = self.accounts[account]
            account.holdBalance -= amount
            account.balance += amount
            return "ok"
        return "Account not found"