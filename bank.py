from account.fisicPersonAccount import PfAccount
from  account.juridicPersonAccount import PjAccount
from account.sharedAccount import SharedAccount
import requests
from flask import request
import os 
import json
class Bank:


    def __init__(self, name):
        self.name = name
        self.accounts = {}
        self.numberAccount = 0;
        self.other_banks = {}

    #Função para preocurar os nomes dos outros bancos com base na variável de ambiente e atualizar o dicionário other_banks
    def findNamesOthersBanks(self):
        bank1_url = os.getenv('BANK_1') 
        bank2_url = os.getenv('BANK_2') 

        other_banks_urls = [bank1_url, bank2_url]
        headers = {'Content-Type': 'application/json'}
        for url in other_banks_urls:
            try:
                response = requests.get(f"http://{url}/bank_name", headers=headers)
                if response.status_code == 200:
                    bank_name_other = response.json().get('name')
                    print(f"Nome do banco obtido: {bank_name_other}")
                    if bank_name_other:
                        self.other_banks[bank_name_other] = url
                else:
                    print(f"Erro ao obter nome do banco: Status Code {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"Erro ao fazer requisição para obter nome do banco: {e}")
    
    #Cadastrando conta pessoa juridica
    def registerPjAccount(self, cnpj, fantasyName, password, nameBank):
        self.numberAccount += 1
        account = PjAccount(self.numberAccount, 0, cnpj, fantasyName, password, nameBank)
        self.accounts[self.numberAccount] = account
        return account

    #Cadastrando conta pessoa fisica
    def registerPfAccount(self, cpf, name, passowrd, nameBank):
        for account in self.accounts.values():
            if isinstance(account, PfAccount) and account.cpf == cpf:
                return None
        self.numberAccount += 1
        account = PfAccount(self.numberAccount, 0, cpf, name, passowrd, nameBank)
        self.accounts[self.numberAccount] = account
        return account

    #Cadastrando conta compartilhada
    def registerSharedAccount(self, cpfs, names, password, nameBank):
        self.numberAccount +=1
        account = SharedAccount(self.numberAccount, 0, cpfs, names, password, nameBank)
        self.accounts[self.numberAccount] = account
        return account

    #Buscar conta a partir do número da conta, verifica se o nome do banco é o dele próprio, se não for, chama o banco respectivo
    def getByAccountNumber(self, numberAccount, bankName):
        self.findNamesOthersBanks()
        if bankName == self.name:
           return self.getByAccountNumberOnSelf(numberAccount)

        bank_url = self.other_banks[bankName] 
        if bank_url is not None:
            headers = {'Content-Type': 'application/json'}
           
            try:
                    response = requests.get(f"http://{bank_url}/accounts/{numberAccount}", headers=headers)
                    response.raise_for_status()
                    return response.json()
            except requests.exceptions.RequestException as req_err:
                print(f"Request Error from {bank_url}: {req_err}")


        return None

    #Chamada interna para buscar a conta no próprio banco
    def getByAccountNumberOnSelf(self, numberAccount):
        numberAccount = int(numberAccount)
        if numberAccount in self.accounts:
            return self.accounts[numberAccount]
        else:
            print(f"Conta com número {numberAccount} não encontrada.")
            return None
        
    #Buscando contas pelo cpf, busca em todos os bancos inclusive no próprio da requisição
    def getAccountByCpf(self, cpf):
        self.findNamesOthersBanks()
        accountsFinded = self.getAccountByCPFOnSelf(cpf)
        otherBanksAccount = self.getOtherBanksAccount(cpf,"cpf")   
        all_accounts = accountsFinded + otherBanksAccount
        return all_accounts

    #Busca conta pelo cpf (pode ser pessoa fisica ou conta compartilhada)
    def getAccountByCPFOnSelf(self, cpf):
        accountsFinded = []
        for account in self.accounts.values():
            if isinstance(account, PfAccount) and account.cpf==cpf:
                accountsFinded.append(account)
            
            elif isinstance(account, SharedAccount) and account.verifyHoldByCpf(cpf):
                accountsFinded.append(account)
        return accountsFinded


    #Busca conta por cnpj no próprio banco e em outros bancos
    def getAccountByCnpj(self, cnpj):
        self.findNamesOthersBanks()
        accountsFinded = self.getAccountByCnpjOnSelf(cnpj)
        otherBanksAccount = self.getOtherBanksAccount(cnpj,"cnpj")        
        all_accounts = accountsFinded + otherBanksAccount
        return all_accounts
    
    #Busca conta por cnpj no próprio banco
    def getAccountByCnpjOnSelf(self, cnpj):
        accountsFinded = []
        for account in self.accounts.values():
            if isinstance(account, PjAccount) and account.cnpj == cnpj:
                accountsFinded.append(account)
        return accountsFinded

    #Prepara para transferência validando o timestemp
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
    
    #Transferência do saldo
    def transfer(self, account, amount):
        if account in self.accounts:
            account = self.accounts[account]
            if account.holdBalance < amount:
                return "insufficient_funds"
            account.holdBalance -= amount
            return "ok"
        return "Account not found"

    #Prepara todos os bancos para transferir
    def prepareAllToTransfer(self, transfers, account_destiny, bank_destiny):

        account = self.getByAccountNumber(account_destiny, bank_destiny) #Verifica existência da conta de destino
        if account :

            prepared = []
            notPrepared = []
            #Valida em todos os bancos se estão prontos para transferir     
            for transfer in transfers:
                print(transfer.bankName)
                if transfer.bankName== self.name:
                    print("tudo certo por aqui")
                    message = self.prepareTransfer (transfer.account, transfer.amount, transfer.timesTemp)
                    if message == "prepared":
                        
                        prepared.append(transfer)
                    else:
                        notPrepared.append(transfer)
                   
                else:
                    bank_url = self.other_banks[transfer.bankName] 
                    if bank_url is not None:
                        headers = {'Content-Type': 'application/json'}
                        
                        body = {
                            "account_id": transfer.account,
                            "amount": transfer.amount
                        }

                        try:
                            response = requests.post(f"http://{bank_url}/prepareOnSelf", headers=headers, data=json.dumps(body))
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

            if len(notPrepared) != 0: #Valida se existe algum banco que não está preparado, se tiver, faz rollback nos que estão preparados

                for transfer in prepared:
                    if transfer.bankName==self.name:
                        message = self.rollback(transfer.account, transfer.amount)

                    else:
                        bank_url = self.other_banks[transfer.bankName]
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
            else: #Commita todos os preparados 
                totalAmount = 0;
                for transfer in prepared:
                    if transfer.bankName==self.name:
                        message = self.transfer(transfer.account, transfer.amount)
                        totalAmount+= transfer.amount

                    else:
                        bank_url = self.other_banks[transfer.bankName]
                        if bank_url is not None:
                            headers = {'Content-Type': 'application/json'}
                            
                            body = {
                                "account_id": transfer.account,
                                "amount": transfer.amount
                            }
                            tryAgain = True;
                            while tryAgain:
                                try:
                                    response = requests.post(f"http://{bank_url}/commit", headers=headers, data=json.dumps(body))
                                    response.raise_for_status()
                                    tryAgain = False
                                    totalAmount+= transfer.amount
                                except requests.exceptions.HTTPError as http_err:
                                    if response.status_code == 404 or response.status_code == 500:
                                        tryAgain = True
                                except requests.exceptions.RequestException as req_err:
                                    print(f"Request Error from {bank_url}: {req_err}")

                self.deposit(account_destiny, totalAmount, bank_destiny)    #Deposita na conta de destino                
                return "Success"

        else:
            return "Transfer destination not found"

    #Deposita na própria conta
    def depositOnSelf(self, account, amount):
        account = int(account)
        account = self.accounts[account]
        
        if account != None: 
            amount = int(amount)           
            account.balance+= amount
            print(account.balance)
            return "deposit"
        else: 
            return "Account not found"
        
    #Deposita com base no nome do banco e a conta fornecida    
    def deposit(self, account, amount, bankName):
        self.findNamesOthersBanks()
        if bankName == self.name:
            return self.depositOnSelf(account, amount)
        
       
        bank_url = self.other_banks[bankName]
        if bank_url is not None:
            headers = {'Content-Type': 'application/json'}
            print('Entrou aqui no deposit url')
            body = {
                "account_id": account,
                "amount": amount
            }
            tryAgain = True; #Fica tentando transferir até conseguir 
            while tryAgain:
                try:
                    response = requests.post(f"http://{bank_url}/account/depositOnSelf", headers=headers, data=json.dumps(body))
                    response.raise_for_status()
                    tryAgain = False
                    return "deposit"
                except requests.exceptions.HTTPError as http_err:
                    if response.status_code == 500:
                        tryAgain = True
                except requests.exceptions.RequestException as req_err:
                    print(f"Request Error from {bank_url}: {req_err}")
            
            return account
        return "Account or Bank not found"

    #Dá rollback no que estava preparado em si próprio        
    def rollback(self, account, amount):
        if account in self.accounts:
            account = self.accounts[account]
            account.holdBalance -= amount
            account.balance += amount
            return "ok"
        return "Account not found"
    
    #Pega as contas de outros bancos com base no tipo de documento e no documento em si
    def getOtherBanksAccount(self, document, type):
        
        headers = {'Content-Type': 'application/json'}


        banks = self.other_banks
        accounts = []
        for bank_url in banks:
            if bank_url != None:
                try:
                    bank_url = banks[bank_url]
                    response = requests.get(f"http://{bank_url}/accountSOnSelf/{type}/{document}", headers=headers)
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
    