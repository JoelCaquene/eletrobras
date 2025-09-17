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

# A chave secreta é carregada da variável de ambiente SECRET_KEY.
# IMPORTANTE: Em produção, o valor vem do Render.
SECRET_KEY = os.getenv('SECRET_KEY')

# O modo de debug é controlado pela variável de ambiente DJANGO_DEBUG.
# É crucial que ela seja 'False' em produção.
DEBUG = os.getenv('DJANGO_DEBUG') == 'True'

# Domínios permitidos para sua aplicação em produção.
# O domínio do seu Render deve estar aqui.
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'eletrobras.onrender.com']


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Suas aplicações
    'eletrobras',

    # Apps de terceiros para deploy
    'cloudinary_storage',
    'cloudinary',
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # WhiteNoise deve vir logo após SecurityMiddleware.
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
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL'),
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
TIME_ZONE = 'Africa/Luanda'
USE_I18N = True
USE_TZ = True


# --- Seção de Arquivos Estáticos ---
# https://docs.djangoproject.com/en/5.2/howto/static-files/

# URL para referenciar arquivos estáticos no seu HTML.
STATIC_URL = 'static/' # Apenas 'static/'

# Pasta para onde os arquivos estáticos serão coletados em produção.
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Pastas de onde o Django deve buscar os arquivos estáticos.
STATICFILES_DIRS = [
    BASE_DIR / 'static',
    BASE_DIR / 'eletrobras/static',
]

# Configuração de armazenamento para arquivos estáticos em produção (WhiteNoise).
# Esta é a chave para o Render servir suas imagens e CSS corretamente.
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# --- Seção de Arquivos de Mídia (Uploads de usuários) ---
MEDIA_URL = '/media/'

# Pasta local para arquivos de mídia (usada em desenvolvimento).
MEDIA_ROOT = BASE_DIR / 'media'

# Configuração de armazenamento para arquivos de mídia em produção (Cloudinary).
# Isso diz ao Django para usar o Cloudinary para uploads.
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# URL do Cloudinary, lida com a conexão e armazenamento das imagens de mídia.
CLOUDINARY_URL = os.getenv('CLOUDINARY_URL')


# Outras configurações
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'eletrobras.Usuario'
LOGIN_URL = 'login'

# Para segurança CSRF em produção, adicione a URL do seu Render.
CSRF_TRUSTED_ORIGINS = ['https://eletrobras.onrender.com']
