from flask import Flask, request, jsonify, render_template
from bank import Bank
from prepareDTO import PrepareDTO
import time
import os

app = Flask(__name__, template_folder='templates', static_folder='static')
bank = Bank("Claudia Bank")

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def process_login():
    data = request.json

    tipo_conta = data.get('tipo_conta')
    password = data.get('password')

    if tipo_conta == 'pessoa_fisica' or tipo_conta == 'compartilhada':
        document = data.get('cpf')
    elif tipo_conta == 'pessoa_juridica':
        document = data.get('cnpj')
    else:
        return jsonify({"error": "Tipo de conta inválido"}), 400

    
    return buscarcontaOnSelfWithPassword(tipo_conta, document, password)

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/contas', methods=['POST'])
def criar_conta():
    data = request.json

    tipo_conta = data.get('tipo_conta')

    if tipo_conta == 'pessoa_fisica':
        password = data.get('password')
        name = data.get('name')
        cpf = data.get('cpf')
        conta = bank.registerPfAccount(cpf, name, password)
    elif tipo_conta == 'pessoa_juridica':
        fantasy_name = data.get('fantasyName')
        cnpj = data.get('cnpj')
        password = data.get('password')
        conta =  bank.registerPjAccount(cnpj, fantasy_name, password)
    elif tipo_conta == 'compartilhada':
        names = data.get('names')
        cpfs = data.get('cpfs')
        password = data.get('password')
        conta = bank.registerSharedAccount(cpfs,names, password)
    else:
        return jsonify({"error": "Tipo de conta inválido"}), 400

    if(conta is None):
        return jsonify({"message": "CPF já utlizado para conta pessoa fisica"}), 400
    return jsonify({"message": f"Conta {tipo_conta} criada com sucesso: {conta}"}), 201


@app.route('/accounts/<type>/<document>', methods=['GET'])
def buscar_conta(type, document):
    if type == 'cpf':
        accounts = bank.getAccountByCpf(document)
    elif type == 'cnpj':
       accounts =  bank.getAccountByCnpj(document)
    else:
        return jsonify({"error": "Tipo de documento inválido. Use 'cpf' ou 'cnpj'"}), 400
    
    serialized_accounts = [account.to_dict() if hasattr(account, 'to_dict') else account for account in accounts]

    return jsonify(serialized_accounts), 200

@app.route('/accountSOnSelf/<type>/<document>', methods=['GET'])
def buscar_contaOnSelf(type, document):
    if type == 'cpf':
        accounts = bank.getAccountByCPFOnSelf(document)
    elif type == 'cnpj':
       accounts =  bank.getAccountByCnpjOnSelf(document)
    else:
        return jsonify({"error": "Tipo de documento inválido. Use 'cpf' ou 'cnpj'"}), 400

    serialized_accounts = [account.to_dict() if hasattr(account, 'to_dict') else account for account in accounts]

    return jsonify(serialized_accounts), 200

@app.route('/accountSOnSelf/<type>/<document>/<password>', methods=['GET'])
def buscarcontaOnSelfWithPassword(type, document, password):
    if type in ['pessoa_fisica', 'compartilhada']:
        accounts = bank.getAccountByCPFOnSelf(document)
        if accounts:
            if type == 'pessoa_fisica':
                if accounts[0].password == password:
                    return jsonify(accounts[0].to_dict()), 200
                else:
                    return jsonify({"error": "Senha incorreta"}), 401
            else:  # compartilhada
                for account in accounts:
                    if account.password == password:
                        return jsonify(account), 200
                return jsonify({"error": "Senha incorreta"}), 401
        else:
            return jsonify({"error": "Conta não encontrada"}), 404
    elif type == 'pessoa_juridica':
        account = bank.getAccountByCnpjOnSelf(document)
        if account:
            if account.password == password:
                return jsonify(account), 200
            else:
                return jsonify({"error": "Senha incorreta"}), 401
        else:
            return jsonify({"error": "Conta não encontrada"}), 404
    else:
        return jsonify({"error": "Tipo de documento inválido. Use 'cpf' ou 'cnpj'"}), 400




@app.route('/accounts/bank/<bankName>/<accountNumber>', methods=['GET'])
def getAccountByNumber(accountNumber, bankName):
    account = bank.getByAccountNumber(accountNumber, bankName)
    if account is None:
        return jsonify({"error": "Conta não encontrada"}), 400 
    
    #serialized_account = [account.to_dict()]
    return jsonify(account), 200

# Chamada interna
@app.route('/accounts/<accountNumber>', methods=['GET'])
def getAccountByNumberOnSelfBank(accountNumber):
    account = bank.getByAccountNumberOnSelf(accountNumber)
    if account is None:
        return jsonify({"error": "Conta não encontrada"}), 400 
    serialized_account = [account.to_dict()]
    return jsonify(serialized_account), 200


@app.route('/prepareOnSelf', methods=['POST'])
def prepareOnSelf():
    data = request.json
    account_id = data['account_id']
    amount = data['amount']
    transaction_timestamp = int(time.time() * 1000)

    message = bank.prepareTransfer(account_id, amount, transaction_timestamp)

    if message == "prepared":
        return jsonify({"status": "prepared"})
    elif message == "conflict":   
        return jsonify({"status": "conflict"}), 409  
    elif message == "insufficient_funds":
        return jsonify({"status": "insufficient_funds"}), 400
    else:
        return jsonify({"error": "Account not found"}), 404


@app.route('/transfer', methods=['POST'])
def transfer():
    data = request.json

    account_destiny=  data.get('account_destiny')
    bank_destiny= data["bank_destiny"]

    results = []
    transfers = data['transfer']
    for item in transfers:
        account_id = item.get('account_id')
        amount = item.get('amount')
        bank_name = item.get('bank_name')
        transaction_timestamp = int(time.time() * 1000)    
        results.append(PrepareDTO(account_id, amount, bank_name, transaction_timestamp))

    message = bank.prepareAllToTransfer(results, account_destiny, bank_destiny)

    if message == "Transfer destination not found":
        return jsonify({"error": "Transfer destination not found"}), 404
    elif message == "Error":
        return jsonify({"error":"Error to transfer amount, any bank reject the request. Consult your balance in your bank"}), 500
    
    return jsonify({"status":"Success"})



@app.route('/account/deposit', methods=['POST'])
def depoiste():
    data = request.json
    account_id = data['account_id']
    bankName = data['bank_name']
    amount = data['amount']
    message = bank.deposit(account_id, amount, bankName)
    if message == "deposit":
        return jsonify({"status": "deposited"}), 200
    else:
        return  jsonify({"error": "Account not found"}), 404


# Chamada Interna
@app.route('/account/depositOnSelf', methods=['POST'])
def depoisteOnSelf():
    data = request.json
    account_id = data['account_id']
    amount = data['amount']
    print('Chegou mami')
    message = bank.depositOnSelf(account_id, amount)
    if message == "deposit":
        return jsonify({"status": "deposited"}), 200
    else:
        return  jsonify({"error": "Account not found"}), 404

@app.route('/commit', methods=['POST'])
def commit():
    data = request.json
    account_id = data['account_id']
    amount = data['amount']

    message = bank.transfer(account_id, amount)
    if message == "ok":
        return jsonify({"status": "committed"})
    elif message == "insufficient_funds":
        return jsonify({"status": "insufficient_funds"}), 400
    else:
        return jsonify({"error": "Account not found"}), 404
    
@app.route('/balance/<type>/<document>', methods=['GET'])
def getBalance(type, document):
    if type == 'cpf':
        accounts = bank.getAccountByCpf(document)
    elif type == 'cnpj':
       accounts =  bank.getAccountByCnpj(document)
    else:
        return jsonify({"error": "Tipo de documento inválido. Use 'cpf' ou 'cnpj'"}), 400
    
    balances = [{"account_number": account.accountNumber, "balance": account.balance} for account in accounts]

    return jsonify(balances), 200 

@app.route('/rollback', methods=['POST'])
def rollback():
    data = request.json
    account_id = data['account_id']
    amount = data['amount']

    message = bank.rollback(account_id, amount)
    if message == 'ok':
        return jsonify({"status": "rolled_back"})
    else:
        return jsonify({"error": "Account not found"}), 404
    
@app.route('/receiveTransfer', methods=['POST'])
def receiveTransfer():
    data = request.json
    account_id = data['account_id']
    amount = data['amount']

    bank.depositOnSelf(account_id, amount)

    return jsonify({"status": "receive"})


if __name__ == '__main__':
    try:
        port = int(os.environ.get('FLASK_PORT', 5000))
        app.run(debug=True, host='0.0.0.0', port=port)
    except Exception:
         app.run(debug=True)
   