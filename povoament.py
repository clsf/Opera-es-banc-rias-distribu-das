import requests

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

# Função para criar uma conta em um banco específico
def criar_conta(usuario, url):
    endpoint = f"{url}/contas"
    response = requests.post(endpoint, json=usuario)
    return response.json()

# Criar contas em todos os bancos para cada usuário
for usuario in usuarios:
    for banco, url in urls.items():
        response = criar_conta(usuario, url)
        print(f"Conta criada para {usuario['name']} no {banco}: {response}")
