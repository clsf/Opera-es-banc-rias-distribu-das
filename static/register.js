$(document).ready(function() {
    // Mostra o formulário adequado baseado no tipo de conta selecionado
    $('#tipoConta').change(function() {
        var tipoConta = $(this).val();

        $('#formPf').hide();
        $('#formPj').hide();
        $('#formShared').hide();

        if (tipoConta === 'pessoa_fisica') {
            $('#formPf').show();
        } else if (tipoConta === 'pessoa_juridica') {
            $('#formPj').show();
        } else if (tipoConta === 'compartilhada') {
            $('#formShared').show();
        }
    });

    // Submete o formulário de criação de conta
    $('#formLogin').submit(function(event) {
        event.preventDefault(); // Evita o comportamento padrão do formulário

        var tipoConta = $('#tipoConta').val();
        var data = {
            tipo_conta: tipoConta
        };

        if (tipoConta === 'pessoa_fisica') {
            data.name = $('#name').val();
            data.cpf = $('#cpf').val();
            data.password = $('#password').val();
        } else if (tipoConta === 'pessoa_juridica') {
            data.fantasyName = $('#fantasyName').val();
            data.cnpj = $('#cnpj').val();
            data.password = $('#passwordPj').val();
        } else if (tipoConta === 'compartilhada') {
            data.names = $('#names').val().split(',');
            data.cpfs = $('#cpfs').val().split(',');
            data.password = $('#passwordShared').val();
        }

        // Envia a requisição para o Flask
        $.ajax({
            url: "/contas", // Modifiquei para a URL relativa
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify(data),
            success: function(response) {
                $('#resultado').html(`<div class="alert alert-success" role="alert">${response.message}</div>`);
            },
            error: function(xhr, status, error) {
                var errorMessage = xhr.responseJSON && xhr.responseJSON.error ? xhr.responseJSON.error : "Erro ao criar conta";
                $('#resultado').html(`<div class="alert alert-danger" role="alert">${errorMessage}</div>`);
            }
        });
    });
});
