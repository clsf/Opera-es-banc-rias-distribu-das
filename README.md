# Problema 2: Operações bancárias distribuídas

## Sumário
- [Introdução](#introdução)
- [Iniciando a Aplicação](#iniciando-a-aplicação)
- [Uso](#uso)
- [Estrutura do Projeto](#estrutura-do-projeto)

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

## Estrutura do Projeto
