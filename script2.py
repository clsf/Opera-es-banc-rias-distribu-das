import requests
import concurrent.futures

# URLs das APIs dos bancos
urls = {
    'BANK1': 'http://localhost:5000',
    'BANK2': 'http://localhost:5001',
    'BANK3': 'http://localhost:5002'
}

# Dados dos usuários (usaremos apenas dois para simular as transferências)
usuario_origem = {"tipo_conta": "pessoa_fisica", "name": "User1", "cpf": "11111111111", "password": "password1"}
usuario_destino = {"tipo_conta": "pessoa_fisica", "name": "User2", "cpf": "22222222222", "password": "password2"}

# Função para realizar transferência entre bancos usando número da conta
def transferir(usuario_origem, usuario_destino, url_origem, banco_origem, url_destino, banco_destino, valor):
    conta_origem = 1  # Conta fixa 1 no BANK1
    conta_destino = 2  # Conta fixa 2 no BANK2

    data = {
        "account_destiny": conta_destino,
        "bank_destiny": banco_destino,
        "transfer": [{"account_id": conta_origem, "amount": valor, "bank_name": banco_origem}]
    }
    response = requests.post(f"{url_origem}/transfer", json=data)
    print(f"Transferência de {valor} de {usuario_origem['name']} ({banco_origem}) para {usuario_destino['name']} ({banco_destino}): {response.json()}")

# Simular a transferência entre BANK1 conta 1 e BANK2 conta 2 três vezes simultaneamente
with concurrent.futures.ThreadPoolExecutor() as executor:
    futures = []
    for _ in range(3):
        futures.append(executor.submit(transferir, usuario_origem, usuario_destino, urls['BANK1'], 'BANK1', urls['BANK2'], 'BANK2', 10))
    for future in concurrent.futures.as_completed(futures):
        future.result()

print("Transferências concluídas.")
