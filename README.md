# Problema 2: Operações bancárias distribuídas

## Sumário
- [Introdução](#introdução)
- [Iniciando a Aplicação](#iniciando-a-aplicação)
- [Uso](#uso)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Construção do Projeto](#contrução-do-projeto)

## Introdução
Este projeto visa resolver o problema 2 do PBL de Concorrência e Conectividade, focando na comunicação entre três ou mais aplicações bancárias configuráveis. Ele possibilita a realização de transações em contas pertencentes ao mesmo usuário, mas em diferentes bancos, abrangendo transferências, pagamentos e depósitos, com garantia de atomicidade das operações. Além disso, o sistema suporta a criação de contas bancárias para pessoas físicas, jurídicas e contas compartilhadas.

## Iniciando a aplicação
O projeto permitir ser inicializado através do docker, a configuração atual permite instanciar três bancos. Para isso é necessário baixar a imagem do projeto no docker, através do seguinte comando:

      docker pull claudiainees/my_images:bank

Após ter baixado a imagem, pode instanciar os três em bancos em terminais distintos executando o seguinte comando:
#### Para o primeiro terminal:

      docker run -it --network=host -e FLASK_PORT=5000 -e BANK_1=0.0.0.0:5001 -e BANK_2=0.0.0.0:5002 -e BANK_NAME=BANK1 claudiainees/my_images:bank
      
Você ṕodar dar o nome que quiser ao banco na variável de ambiente "BANK_NAME". O IP e a porta das variáveos "BANK_1" e "BANK_2" devem ser alteradas caso as portas já estejam em uso, ou vá testar as aplicações em computadores distintos. 

#### Para o segundo terminal:

      docker run -it --network=host -e FLASK_PORT=5001 -e BANK_1=0.0.0.0:5000 -e BANK_2=0.0.0.0:5002 -e BANK_NAME=BANK2 claudiainees/my_images:bank

#### Para o terceiro terminal:

      docker run -it --network=host -e FLASK_PORT=5002 -e BANK_1=0.0.0.0:5000 -e BANK_2=0.0.0.0:5001 -e BANK_NAME=BANK3 claudiainees/my_images:bank

Assim, todas as aplicações dos bancos vão ser iniciadas em cada porta escolhida.

## Uso
### 1. Criação da conta
Para a criação da conta é necessário que o usuário esteja na url [http://localhost:5000/register](http://localhost:5000/register) modificando apenas o número da porta em que aplicação foi inicializada para realizar o cadastro em bancos distintos. 
<a name="tela cadastro"></a>
<div align="center">
  <img src="/img/CricacaoConta.png" alt="" width="700">
   <p>
      Figura 1: Criação de conta.
    </p>
</div>

Na criação de conta de pessoa jurídica é necessário informar apenas o nome fantasia, cnpj e a senha de acesso para a conta:
<a name="tela cadastro pj"></a>
<div align="center">
  <img src="img/criacaopj.png" alt="" width="700">
   <p>
      Figura 2: Criação de conta pessoa jurídica.
    </p>
</div>

E o mesmo se aplica para criação de contas compartilhadas, sendo necessário informar os cpfs dos responsáveis por vírgula, assim como o nome dos mesmos:
<a name="tela cadastro compartilhada"></a>
<div align="center">
  <img src="img/criacaoCompartilhada.png" alt="" width="700">
   <p>
      Figura 3: Criação de conta compartilhada.
    </p>
</div>

Ao realizar o cadastro será exibida uma mensagem de sucesso, e estará pronto para fazer o login:
<a name="tela sucesso cadastro"></a>
<div align="center">
  <img src="img/contaCriada.png" alt="" width="700">
   <p>
      Figura 4: Conta criada com sucesso.
    </p>
</div>

### 2. Login
Após ter realizado o cadastro é possível realizar o login da conta utilizando o a url  [http://localhost:5000/login](http://localhost:5000/login). Deverá escolher o tipo de conta, o cpf/cnpj cadastrado e a senha. Caso insira as informações corretamente será direcionado para a página principal:
<a name="tela login"></a>
<div align="center">
  <img src="img/logado.png" alt="" width="700">
   <p>
      Figura 5: Página incial após logado.
    </p>
</div>

### 4. Depósito
Para realizar um depósito, deve clicar no botão de depósito na página inicial e preencher as informações da conta que você deseja depositar:
<a name="tela depósito"></a>
<div align="center">
  <img src="img/depósito.png" alt="" width="700">
   <p>
      Figura 6: Página após depósito concluído com sucesso.
    </p>
</div>

### 5. Transferência/Pagamento
Para realizar uma transferência, deve clicar no botão de transferência na página inicial e preencher as informações da conta de destino. Caso tenha outras contas em bancos distintos ela irá aparecer nessa tela possibilitando a retirada das contas que estão em outros bancos para que realize a transação:
<a name="tela transferencia"></a>
<div align="center">
  <img src="img/telaTransferencia.png" alt="" width="700">
   <p>
      Figura 7: Página de transferência.
    </p>
</div>

Ao preencher as informações de forma correta e clicar em transferir, uma mensagem de sucesso será exibida, e o saldo terá sido removido da conta selecionada:
<a name="tela transferencia concluida"></a>
<div align="center">
  <img src="img/tranferenciaRealizada.png" alt="" width="700">
   <p>
      Figura 8: Página de transferência realizada.
    </p>
</div>

Na conta de destino irá aparecer o valor transferido, é necessário a atualização da tela:
<a name="tela transferencia recebida"></a>
<div align="center">
  <img src="img/recebimentoTransferência.png" alt="" width="700">
   <p>
      Figura 8: Página do recebimento da transferência.
    </p>
</div>

## Estrutura do Projeto
O projeto possui a seguinte estrutura:
- Account: Na pasta [account](./account) possui as classes que definem as características de cada conta (pessoa física, jurídica ou conta compartilhada)
- Bank: Na classe [bank](./bank.py) possui todos os atributos e métodos necessários para o funcionamento do banco (como criação de contas, busca de contas, trasnferências, depósitos etc)
- Controller: No controller [endpointTest](./endpointTest.py) possui as rotas para cada funcionalidade do banco, para além de administrar qual dever ser a tela exibida. 

## Construção do projeto
#### Utilização do protocolo HTTP para comunicação entre os bancos
#### Concorrência entre as aplicações
#### Algoritmo Two-Phase-Commit (2PC) e uso do artifício Timestemp
