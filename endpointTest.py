from flask import Flask, request, jsonify
from bank import Bank
import time


app = Flask(__name__)
bank = Bank("Claudia Bank")


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


@app.route('/contas/<tipo>/<documento>', methods=['GET'])
def buscar_conta(tipo, documento):
    if tipo == 'cpf':
        accounts = bank.getAccountByCpf(documento)
    elif tipo == 'cnpj':
       accounts =  bank.getAccountByCnpj(documento)
    else:
        return jsonify({"error": "Tipo de documento inválido. Use 'cpf' ou 'cnpj'"}), 400

    serialized_accounts = [account.__dict__ for account in accounts]

    return jsonify(serialized_accounts), 200


@app.route('/prepare', methods=['POST'])
def prepare():
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
    
@app.route('/contas/deposit', methods=['POST'])
def depoiste():
    data = request.json
    account_id = data['account_id']
    amount = data['amount']
    message = bank.deposite(account_id, amount)
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

if __name__ == '__main__':
    app.run(debug=True)