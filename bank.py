from account.fisicPersonAccount import PfAccount
from  account.juridicPersonAccount import PjAccount
from account.sharedAccount import SharedAccount
import requests
import os 
import json
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


    def getByAccountNumber(self, numberAccount, bankName):
        account = None;
        if bankName == "BANK_0":
            numberAccount = int(numberAccount)
            if numberAccount in self.accounts:
                return self.accounts[numberAccount]
            else:
                print(f"Conta com número {numberAccount} não encontrada.")
                return None

        bank_url = os.getenv(bankName) 
        if bank_url is not None:
            headers = {'Content-Type': 'application/json'}
            params = {'numberAccount': numberAccount}

            try:
                    response = requests.get(f"http://{bank_url}/accounts/{numberAccount}", headers=headers, params=params)
                    response.raise_for_status()
                    account.extend(response.json())
            except requests.exceptions.HTTPError as http_err:
                if response.status_code == 400 or response.status_code == 500:
                    account = None
            except requests.exceptions.RequestException as req_err:
                print(f"Request Error from {bank_url}: {req_err}")
            
            return account

        return None


        

    def getAccountByCpf(self, cpf):
        accountsFinded = []
        for account in self.accounts.values():
            if isinstance(account, PfAccount) and account.cpf==cpf:
                accountsFinded.append(account)
            
            elif isinstance(account, SharedAccount) and account.verifyHoldByCpf(cpf):
                accountsFinded.append(account)
        
        otherBanksAccount = Bank.getOtherBanksAccount("cpf", cpf)        
        all_accounts = accountsFinded + otherBanksAccount
        return all_accounts

    def getAccountByCnpj(self, cnpj):
        accountsFinded = []
        for account in self.accounts.values():
            if isinstance(account, PjAccount) and account.cnpj == cnpj:
                accountsFinded.append(account)

        otherBanksAccount = Bank.getOtherBanksAccount("cnpj", cnpj)        
        all_accounts = accountsFinded + otherBanksAccount
        return all_accounts
    
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

    def prepareAllToTransfer(self, transfers, account_destiny, bank_destiny):
        account = self.getByAccountNumber(account_destiny, bank_destiny)
        if account :

            prepared = []
            notPrepared = []

            for transfer in transfers:
                print(transfer.bankName)
                if transfer.bankName=="BANK_0":
                    message = self.prepareTransfer (transfer.account, transfer.amount, transfer.timesTemp)
                    if message == "prepared":
                        prepared.append(transfer)
                    else:
                        notPrepared.append(transfer)
                   
                else:
                    bank_url = os.getenv(transfer.bankName) 
                    if bank_url is not None:
                        headers = {'Content-Type': 'application/json'}
                        
                        body = {
                            "account_id": transfer.account,
                            "amount": transfer.amount
                        }

                        try:
                            response = requests.get(f"http://{bank_url}/prepareOnSelf", headers=headers, data=json.dumps(body))
                            response.raise_for_status()
                            prepared.append(transfer)   
                        except requests.exceptions.HTTPError as http_err:
                            if response.status_code == 400 or response.status_code == 500:
                                notPrepared.append(transfer)   
                        except requests.exceptions.RequestException as req_err:
                            print(f"Request Error from {bank_url}: {req_err}")
                            notPrepared.append(transfer)

                    else:
                        notPrepared.append(transfer)    

            if len(notPrepared) != 0:

                for transfer in prepared:
                    if transfer.bankName=="BANK_0":
                        message = self.rollback(transfer.account, transfer.amount)

                    else:
                        bank_url = os.getenv(transfer.bankName) 
                        if bank_url is not None:
                            headers = {'Content-Type': 'application/json'}
                            
                            body = {
                                "account_id": transfer.account,
                                "amount": transfer.amount
                            }
                            tryAgain = True;
                            while tryAgain:
                                try:
                                    response = requests.get(f"http://{bank_url}/rollback", headers=headers, data=json.dumps(body))
                                    response.raise_for_status()
                                    tryAgain = False
                                except requests.exceptions.HTTPError as http_err:
                                    if response.status_code == 404 or response.status_code == 500:
                                        tryAgain = True
                                except requests.exceptions.RequestException as req_err:
                                    print(f"Request Error from {bank_url}: {req_err}")
                                    

                return "Error"
            else:
                totalAmount = 0;
                for transfer in prepared:
                    if transfer.bankName=="BANK_0":
                        message = self.transfer(transfer.account, transfer.amount)
                        totalAmount+= transfer.amount

                    else:
                        bank_url = os.getenv(transfer.bankName) 
                        if bank_url is not None:
                            headers = {'Content-Type': 'application/json'}
                            
                            body = {
                                "account_id": transfer.account,
                                "amount": transfer.amount
                            }
                            tryAgain = True;
                            while tryAgain:
                                try:
                                    response = requests.get(f"http://{bank_url}/commit", headers=headers, data=json.dumps(body))
                                    response.raise_for_status()
                                    tryAgain = False
                                    totalAmount+= transfer.amount
                                except requests.exceptions.HTTPError as http_err:
                                    if response.status_code == 404 or response.status_code == 500:
                                        tryAgain = True
                                except requests.exceptions.RequestException as req_err:
                                    print(f"Request Error from {bank_url}: {req_err}")

                self.deposit(account_destiny, totalAmount, bank_destiny)                    
                return "Success"

        else:
            return "Transfer destination not found"

    def depositOnSelf(self, account, amount):
        account = int(account)
        account = self.accounts[account]
        if account != None:            
            account.balance+= amount
            return "deposit"
        else: 
            return "Account not found"
        
        
    def deposit(self, account, amount, bankName):
        if bankName == "BANK_0":
            return self.depositOnSelf(account, amount)
        
        bank_url = os.getenv(bankName) 
        if bank_url is not None:
            headers = {'Content-Type': 'application/json'}

            body = {
                "account_id": account,
                "amount": amount
            }

            try:
                response = requests.get(f"http://{bank_url}/accounts/depositOnSelf", headers=headers, data=json.dumps(body))
                response.raise_for_status()
                return "deposit"
            except requests.exceptions.HTTPError as http_err:
                if response.status_code == 400 or response.status_code == 500:
                    return "Account not found"
            except requests.exceptions.RequestException as req_err:
                print(f"Request Error from {bank_url}: {req_err}")
            
            return account
        return "Account or Bank not found"
            
    def rollback(self, account, amount):
        if account in self.accounts:
            account = self.accounts[account]
            account.holdBalance -= amount
            account.balance += amount
            return "ok"
        return "Account not found"
    
    def getOtherBanksAccount(document, type):
        bank1_url = os.getenv('BANK1_URL') 
        bank2_url = os.getenv('BANK2_URL')

        headers = {'Content-Type': 'application/json'}

        params = {'type': type,'document': document}

        banks = [bank1_url, bank2_url]
        accounts = []

        for bank_url in banks:
            if bank1_url != None:
                try:
                    response = requests.get(f"http://{bank_url}/accounts/{type}/{document}", headers=headers, params=params)
                    response.raise_for_status()
                    accounts.extend(response.json())
                except requests.exceptions.HTTPError as http_err:
                    if response.status_code == 400:
                        print(f"400 Bad Request Error from {bank_url}: {http_err}")
                    elif response.status_code == 500:
                        print(f"500 Internal Server Error from {bank_url}: {http_err}")
                    else:
                        print(f"HTTP Error from {bank_url}: {http_err}")
                except requests.exceptions.RequestException as req_err:
                    print(f"Request Error from {bank_url}: {req_err}")

        return accounts
    