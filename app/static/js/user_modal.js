// Função para abrir o modal para cadastro
document.getElementById('openRegisterModal').addEventListener('click', function() {
    document.getElementById('userModalLabel').innerText = 'Cadastrar Usuário';
    document.getElementById('submitButton').innerText = 'Cadastrar';
    document.getElementById('userForm').action = '/manage_users'; // Certifique-se de usar a URL correta
    document.getElementById('form-username').value = '';  // Limpar o campo
    document.getElementById('form-email').value = '';  // Limpar o campo
    document.getElementById('form-password').value = '';  // Limpar o campo
    document.getElementById('form-confirm').value = '';  // Limpar o campo
    var modal = new bootstrap.Modal(document.getElementById('userModal'));
    modal.show();
});

// Função para abrir o modal para editar
document.querySelectorAll('.editUserBtn').forEach(button => {
    button.addEventListener('click', function() {
        document.getElementById('userModalLabel').innerText = 'Editar Usuário';
        document.getElementById('submitButton').innerText = 'Salvar Alterações';
        var userId = this.getAttribute('data-id');
        var username = this.getAttribute('data-username');
        var email = this.getAttribute('data-email');
        document.getElementById('userForm').action = `/edit_user/${userId}`;
        document.getElementById('form-username').value = username;  // Preencher o campo
        document.getElementById('form-email').value = email;  // Preencher o campo
        var modal = new bootstrap.Modal(document.getElementById('userModal'));
        modal.show();
    });
});
