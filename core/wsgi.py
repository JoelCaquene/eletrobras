"""
WSGI config for eletrobras project.

It exposes the WSGI callable as a module-level variable named ``application``.

Para mais informações, veja:
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise # Importa WhiteNoise

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

application = get_wsgi_application()

# Envolve a aplicação WSGI do Django com WhiteNoise.
# Isso garante que WhiteNoise possa servir arquivos estáticos em produção.
application = WhiteNoise(application)
