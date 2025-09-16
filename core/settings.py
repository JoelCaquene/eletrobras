"""
Django settings for eletrobras project.
Configurado para Deploy no Heroku.
"""

from pathlib import Path
import os
import dotenv
import dj_database_url

# Carrega variáveis de ambiente do arquivo .env (apenas para desenvolvimento local)
dotenv.load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# A chave secreta é carregada da variável de ambiente SECRET_KEY.
# O Heroku deve ter essa variável configurada.
SECRET_KEY = os.getenv('SECRET_KEY')

# O modo de debug é controlado pela variável de ambiente DJANGO_DEBUG.
# É crucial que ela seja 'False' em produção.
# Se a variável não estiver definida no Heroku, o padrão é False.
DEBUG = os.getenv('DJANGO_DEBUG', 'False') == 'True'


# Domínios permitidos para sua aplicação em produção.
# Adicione 'SEU-APP.herokuapp.com' e use '*' temporariamente para o deploy inicial.
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '.herokuapp.com'] # Permite qualquer subdomínio do Heroku
# Se você tiver um nome específico (ex: 'eletrobras-app.herokuapp.com'), adicione-o aqui.


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Servidor Web para Heroku
    'gunicorn', 

    # Suas aplicações
    'eletrobras',

    # Apps de terceiros para deploy
    'cloudinary_storage',
    'cloudinary',
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # WhiteNoise deve vir logo após SecurityMiddleware para servir arquivos estáticos.
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


ROOT_URLCONF = 'core.urls'
WSGI_APPLICATION = 'core.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Pasta para templates globais
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# Configuração do Banco de Dados
# O Heroku usa PostgreSQL em produção, mas esta configuração suporta SQLite localmente
# e o DATABASE_URL do Heroku em produção.
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL', f'sqlite:///{BASE_DIR}/db.sqlite3'),
        conn_max_age=600
    )
}

# Validação de Senha e Autenticação de Usuário
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Configurações de Internacionalização
LANGUAGE_CODE = 'pt-br'
# Mantenha o fuso horário local, mas Heroku geralmente usa UTC.
TIME_ZONE = 'UTC' 
USE_I18N = True
USE_TZ = True


# --- Seção de Arquivos Estáticos ---
# https://docs.djangoproject.com/en/5.2/howto/static-files/

# URL para referenciar arquivos estáticos no seu HTML.
STATIC_URL = '/static/' 

# Pasta para onde os arquivos estáticos serão coletados em produção (MANDATÓRIO para WhiteNoise).
# Deve apontar para a pasta 'staticfiles' que WhiteNoise irá servir.
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Pastas de onde o Django deve buscar os arquivos estáticos (além das pastas 'static' das apps).
STATICFILES_DIRS = [
    BASE_DIR / 'static',
    BASE_DIR / 'eletrobras/static',
]

# Configuração de armazenamento para arquivos estáticos em produção (WhiteNoise).
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# --- Seção de Arquivos de Média (Uploads de usuários) ---
MEDIA_URL = '/media/'

# Pasta local para arquivos de mídia (usada em desenvolvimento).
MEDIA_ROOT = BASE_DIR / 'media'

# Configuração de armazenamento para arquivos de mídia em produção (Cloudinary).
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# URL do Cloudinary, lida com a conexão e armazenamento das imagens de mídia.
CLOUDINARY_URL = os.getenv('CLOUDINARY_URL')


# Outras configurações
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'eletrobras.Usuario'
LOGIN_URL = 'login'

# Para segurança CSRF em produção, inclua o domínio do Heroku.
CSRF_TRUSTED_ORIGINS = ['https://*.herokuapp.com'] # Permite qualquer app do Heroku

# Configuração para que o Django confie nos headers de proxy do Heroku
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
