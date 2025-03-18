# login app generico


## Necessaário um .env para iniciar a aplicação criando um usuário admin do sistema

.env
USUARIO="user"
SENHA="senha"
EMAIL="email@exemplo.com"

## Necessário um config.py para gerar o banco de dados

config.py
import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'supersecretkey'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "SuaSenhaAqui")