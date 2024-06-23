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

    // Submete o formulário de login
    $('#formLogin').submit(function(event) {
        event.preventDefault(); // Evita o comportamento padrão do formulário

        var tipoConta = $('#tipoConta').val();
        var data = {
            tipo_conta: tipoConta,            
        };

        // Adiciona dados específicos com base no tipo de conta
        if (tipoConta === 'pessoa_fisica') {
            data.cpf = $('#cpf').val();
            data.password = $('#password').val();
        } else if (tipoConta === 'pessoa_juridica') {
            data.cnpj = $('#cnpj').val();
            data.password = $('#passwordPj').val();
        } else if (tipoConta === 'compartilhada') {
            data.cpf = $('#cpfShared').val();
            data.password = $('#passwordShared').val();
        }
        console.log(data)
        // Envia a requisição para o Flask
        $.ajax({
            url: "/login", // Rota corrigida para o endpoint de login
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify(data),
            success: function(response) {
                sessionStorage.setItem('account', JSON.stringify(response));
                window.location.href = "/home";
                if (tipoConta === 'pessoa_fisica') {
                    sessionStorage.setItem('document', data.cpf);                   
                } else if (tipoConta === 'pessoa_juridica') {
                    sessionStorage.setItem('document', data.cnpj);                    
                } else if (tipoConta === 'compartilhada') {
                    sessionStorage.setItem('document', data.cpf);;                   
                }
            },
            error: function(xhr, status, error) {
                var errorMessage = xhr.responseJSON && xhr.responseJSON.error ? xhr.responseJSON.error : "Erro ao fazer login";
                $('#resultado').html(`<div class="alert alert-danger" role="alert">${errorMessage}</div>`);
            }
        });
    });
});
