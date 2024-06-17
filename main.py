from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'

# Banco de dados em memória para usuários (para simplicidade)
users = {}

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username]['password'] == password:
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Nome de usuário ou senha inválidos.', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        account_type = request.form['account_type']
        username = request.form['username']
        password = request.form['password']
        if username in users:
            flash('Nome de usuário já existe.', 'danger')
        else:
            if account_type == 'pessoa_fisica':
                nome = request.form['nome']
                cpf = request.form['cpf']
                users[username] = {
                    'password': password,
                    'account_type': account_type,
                    'nome': nome,
                    'cpf': cpf
                }
            elif account_type == 'pessoa_juridica':
                nome_fantasia = request.form['nome_fantasia']
                cnpj = request.form['cnpj']
                users[username] = {
                    'password': password,
                    'account_type': account_type,
                    'nome_fantasia': nome_fantasia,
                    'cnpj': cnpj
                }
            elif account_type == 'compartilhada':
                shared_names = request.form.getlist('shared_names[]')
                shared_cpfs = request.form.getlist('shared_cpfs[]')
                users[username] = {
                    'password': password,
                    'account_type': account_type,
                    'shared_info': list(zip(shared_names, shared_cpfs))
                }
            flash('Registrado com sucesso! Faça login.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True)
