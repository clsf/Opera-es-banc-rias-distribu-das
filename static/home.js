$(document).ready(function() {
    // Assume que a variável `account` contém o objeto da conta do usuário
    var account = {
        id: 123, // Substitua com os dados reais
        balance: 1000.00 // Substitua com os dados reais
    };

    // Função para exibir o saldo da conta
    function displayBalance(account) {
        $('#accountBalance').text(`Saldo: R$ ${account.balance.toFixed(2)}`);
    }

    // Exibir o saldo ao carregar a página
    displayBalance(account);

    // Mostra o formulário de depósito ao clicar no botão
    $('#depositButton').click(function() {
        $('#depositForm').toggle();
    });

    // Submete o formulário de depósito
    $('#depositForm').submit(function(event) {
        event.preventDefault(); // Evita o comportamento padrão do formulário

        var data = {
            account_id: account.id, // Usa o ID da conta do objeto `account`
            amount: parseFloat($('#depositAmount').val()),
            bank_name: $('#depositBankName').val()
        };

        $.ajax({
            url: "/account/deposit",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify(data),
            success: function(response) {
                $('#depositResult').html(`<div class="alert alert-success" role="alert">Depósito realizado com sucesso</div>`);
                // Atualiza o saldo após o depósito
                account.balance += data.amount;
                displayBalance(account);
            },
            error: function(xhr, status, error) {
                var errorMessage = xhr.responseJSON && xhr.responseJSON.error ? xhr.responseJSON.error : "Erro ao realizar depósito";
                $('#depositResult').html(`<div class="alert alert-danger" role="alert">${errorMessage}</div>`);
            }
        });
    });
});
