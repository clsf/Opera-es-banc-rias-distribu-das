import requests
import concurrent.futures
import time

# URLs das APIs dos bancos
urls = {
    'BANK1': 'http://localhost:5000',
    'BANK2': 'http://localhost:5001',
    'BANK3': 'http://localhost:5002'
}

# Dados dos usuários
usuarios = [
    {"tipo_conta": "pessoa_fisica", "name": "User1", "cpf": "11111111111", "password": "password1"},
    {"tipo_conta": "pessoa_fisica", "name": "User2", "cpf": "22222222222", "password": "password2"},
    {"tipo_conta": "pessoa_fisica", "name": "User3", "cpf": "33333333333", "password": "password3"}
]

# Mapear os números de conta dos usuários por banco
contas = {url: {} for url in urls.values()}

# Contador para números de conta por banco
contador_contas = {url: 1 for url in urls.values()}

# Função para criar uma conta em um banco
def criar_conta(usuario, url):
    global contador_contas
    
    endpoint = f"{url}/contas"
    response = requests.post(endpoint, json=usuario)
    if response.status_code == 201:
        conta_id = response.json().get('conta_id')
        if usuario['cpf'] not in contas[url]:
            contas[url][usuario['cpf']] = contador_contas[url]
            print(f"Número de conta para {usuario['name']} no banco {url}: {contas[url][usuario['cpf']]}")
            contador_contas[url] += 1

# Função para realizar depósito usando número da conta
def depositar(usuario, url, banco, valor):
    conta_numero = contas[url].get(usuario['cpf'])
    if not conta_numero:
        print(f"Conta não encontrada para o usuário {usuario['name']} no banco {banco}")
        return

    data = {
        "account_id": conta_numero,
        "bank_name": banco,
        "amount": valor
    }
    response = requests.post(f"{url}/account/deposit", json=data)
    print(f"Depósito de {valor} para {usuario['name']} no banco {banco}: {response.json()}")

# Função para realizar transferência entre bancos usando número da conta
def transferir_especifico(usuario_origem, usuario_destino, url_origem, banco_origem, url_destino, banco_destino, valor):
    conta_origem = contas[url_origem].get(usuario_origem['cpf'])
    conta_destino = contas[url_destino].get(usuario_destino['cpf'])
    if not conta_origem or not conta_destino:
        print(f"Conta não encontrada para realizar a transferência entre {usuario_origem['name']} e {usuario_destino['name']}")
        return

    data = {
        "account_destiny": conta_destino,
        "bank_destiny": banco_destino,
        "transfer": [{"account_id": conta_origem, "amount": valor, "bank_name": banco_origem}]
    }
    response = requests.post(f"{url_origem}/transfer", json=data)
    print(f"Transferência de {valor} de {usuario_origem['name']} ({banco_origem}) para {usuario_destino['name']} ({banco_destino}): {response.json()}")

# Criar contas seguindo a sequência de CPFs nos três bancos
with concurrent.futures.ThreadPoolExecutor() as executor:
    futures = []
    for usuario in usuarios:
        for banco, url in urls.items():
            futures.append(executor.submit(criar_conta, usuario, url))
    for future in concurrent.futures.as_completed(futures):
        future.result()

# Esperar um pouco para garantir que as contas sejam criadas antes de prosseguir
time.sleep(5)

# # Realizar depósitos somente na primeira conta de cada usuário em cada banco
# with concurrent.futures.ThreadPoolExecutor() as executor:
#     futures = []
#     for i, (banco, url) in enumerate(urls.items()):
#         futures.append(executor.submit(depositar, usuarios[i], url, banco, 10))
#     for future in concurrent.futures.as_completed(futures):
#         future.result()

# print("Depósitos concluídos.")

# # Simular a transferência entre BANK1 conta 1 e BANK2 conta 2 duas vezes simultaneamente
# with concurrent.futures.ThreadPoolExecutor() as executor:
#     futures = []
#     for _ in range(2):
#         futures.append(executor.submit(transferir_especifico, usuarios[0], usuarios[1], urls['BANK1'], 'BANK1', urls['BANK2'], 'BANK2', 10))
#     for future in concurrent.futures.as_completed(futures):
#         future.result()

# print("Transferências concluídas.")
