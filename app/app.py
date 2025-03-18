from flask import Flask, render_template, redirect, url_for, flash, abort
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from functools import wraps
from config import Config
from models import db, User
from dotenv import load_dotenv
from forms import LoginForm, RegisterForm, ProfileForm


import os
import locale


# Carregar variáveis do arquivo .env
load_dotenv()

# Variáveis de ambiente
usuario = os.getenv("USUARIO")
senha = os.getenv("SENHA")
email = os.getenv("EMAIL")

# Criar a aplicação Flask
app = Flask(__name__)
app.config.from_object(Config)


# Inicializando o banco de dados com o método init_app
db.init_app(app)  # Inicializa o SQLAlchemy com a aplicação Flask

# Inicializa o Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# Definir o locale para a moeda brasileira (R$)
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Função para criar administrador
def create_admin():
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username=usuario, email=email, role='admin')
        admin.set_password(senha)
        db.session.add(admin)
        db.session.commit()


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Você não tem permissão para acessar esta página.', 'danger')
            return redirect(url_for('dashboard'))  # Redireciona para o dashboard
        return f(*args, **kwargs)
    return decorated_function

# Capturando erro 403
@app.errorhandler(403)
def forbidden(e):
    flash('Você não tem permissão para acessar esta página.', 'danger')
    return redirect(url_for('dashboard'))

@app.route('/')
@login_required
def index():
    return render_template('dashboard.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Login bem-sucedido!', 'success')  # Mensagem de sucesso com categoria 'success'
            return redirect(url_for('dashboard'))
        else:
            flash('Usuário ou senha inválidos.', 'danger')  # Mensagem de erro com categoria 'danger'
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout realizado com sucesso!', 'success')  # Mensagem de sucesso com categoria 'success'
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
@admin_required
@login_required
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Verificar se o username ou email já existem
        existing_user = User.query.filter((User.username == form.username.data) | (User.email == form.email.data)).first()
        if existing_user:
            flash('Usuário ou e-mail já está cadastrado.', 'danger')  # Mensagem de erro
        else:
            # Se não existir, continuar com o cadastro
            user = User(username=form.username.data, email=form.email.data, role='user')
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Usuário registrado com sucesso!', 'success')  # Mensagem de sucesso
            return redirect(url_for('manage_users'))
    
    return render_template('user/register.html', form=form)

@app.route('/edit_user/<int:user_id>', methods=['POST'])
@admin_required
@login_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = RegisterForm()

    # Se o formulário for validado, atualize o usuário
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        if form.password.data:
            user.set_password(form.password.data)  # Atualiza a senha se for inserida
        db.session.commit()
        flash('Usuário atualizado com sucesso!', 'success')
        return redirect(url_for('manage_users'))

    flash('Erro ao editar usuário.', 'danger')
    return redirect(url_for('manage_users'))

@app.route('/delete_user/<int:user_id>', methods=['POST'])
@admin_required
@login_required
def delete_user(user_id):
    # Obtém o usuário a ser excluído
    user = User.query.get_or_404(user_id)

    # Verificar se o usuário a ser excluído é o último administrador
    if user.role == 'admin':
        # Verificar se há pelo menos um outro administrador
        admin_count = User.query.filter_by(role='admin').count()

        if admin_count <= 1:
            flash('Não é possível excluir o último administrador.', 'danger')
            return redirect(url_for('manage_users'))  # Redireciona para a página de gestão de usuários

    # Se passou pela verificação, exclui o usuário
    db.session.delete(user)
    db.session.commit()
    flash(f'O usuário {user.username} foi excluído com sucesso.', 'success')
    return redirect(url_for('manage_users'))


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    user = current_user

    if form.validate_on_submit():
        user.email = form.email.data
        user.set_password(form.password.data)
        db.session.commit()
        flash('Perfil atualizado com sucesso!', 'success')
        return redirect(url_for('profile'))

    form.email.data = user.email
    return render_template('user/profile.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/manage_users', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_users():
    users = User.query.all()  # Obtém todos os usuários
    form = RegisterForm()  # Instancia o formulário de cadastro de usuário
    
    # Se o formulário de cadastro for enviado e validado
    if form.validate_on_submit():
        # Verifica se o usuário ou e-mail já existe
        existing_user = User.query.filter((User.username == form.username.data) | (User.email == form.email.data)).first()
        if existing_user:
            flash('Usuário ou e-mail já cadastrado.', 'danger')
        else:
            # Cria e cadastra o novo usuário
            user = User(username=form.username.data, email=form.email.data, role='user')
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Usuário cadastrado com sucesso!', 'success')
        return redirect(url_for('manage_users'))  # Redireciona para a mesma página após o cadastro

    # Renderiza a página passando a lista de usuários e o formulário de cadastro
    return render_template('user/manage_users.html', users=users, form=form)



@app.route('/set_role/<int:user_id>/<role>', methods=['POST'])
@login_required
@admin_required
def set_role(user_id, role):
    user = User.query.get_or_404(user_id)  # Obtém o usuário pelo ID ou retorna erro 404
    
    # Verificar se o usuário a ser excluído é o último administrador
    if user.role == 'admin':
        # Verificar se há pelo menos um outro administrador
        admin_count = User.query.filter_by(role='admin').count()

        if admin_count <= 1:
            flash('Não é possível remover papel do último administrador.', 'danger')
            return redirect(url_for('manage_users'))  # Redireciona para a página de gestão de usuários

    
    if role not in ['user', 'admin']:
        flash('Papel inválido.', 'danger')
        return redirect(url_for('manage_users'))

    user.role = role  # Atualiza o papel do usuário
    db.session.commit()  # Salva as alterações no banco de dados

    flash(f'O papel de {user.username} foi alterado para {role}.', 'success')
    return redirect(url_for('manage_users'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_admin()  # Criando o administrador aqui
    app.run(debug=True)

