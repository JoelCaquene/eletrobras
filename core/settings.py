"""
Django settings for eletrobras project.
"""

from pathlib import Path
import os
import dotenv
import dj_database_url

# Carrega variáveis de ambiente do arquivo .env
dotenv.load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
# Usa a variável de ambiente para controlar o DEBUG
DEBUG = os.getenv('DJANGO_DEBUG') == 'True'

# Domínios permitidos para acessar sua aplicação
# Adicione o domínio do seu Render aqui
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'eletrobras.onrender.com']

# Aplicações adicionadas e apps para Cloudinary e WhiteNoise
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Suas aplicações
    'eletrobras', # O nome da sua aplicação que contém os modelos e views

    # Apps de terceiros para deploy
    'cloudinary_storage',
    'cloudinary',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # WhiteNoise deve vir logo após SecurityMiddleware
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Aponte para a sua pasta de projeto principal, 'core'
ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')], # Adicionado para templates globais
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

# Aponte para a sua pasta de projeto principal, 'core'
WSGI_APPLICATION = 'core.wsgi.application'

# --------------------------------------------------------------
# Início da seção para configuração do banco de dados em produção
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL'),
        conn_max_age=600
    )
}
# Fim da seção de configuração de banco de dados
# --------------------------------------------------------------

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'Africa/Luanda'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Configuração de armazenamento de arquivos (ativado para produção)
# Use Cloudinary para arquivos de mídia (uploads de usuários)
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# Use WhiteNoise para arquivos estáticos em produção (CSS, JS, etc.)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# Configurações do Cloudinary (necessárias para produção)
CLOUDINARY_URL = os.getenv('CLOUDINARY_URL')


# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Modelos de Autenticação
AUTH_USER_MODEL = 'eletrobras.Usuario'

# URL para onde o Django redireciona para o login
LOGIN_URL = 'login'

# Para segurança CSRF em produção
CSRF_TRUSTED_ORIGINS = ['https://eletrobras.onrender.com']
