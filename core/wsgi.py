"""
WSGI config for CIGNA_GROUP project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

# Altere esta linha para apontar para o seu pacote de projeto principal
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CIGNA_GROUP.settings')

application = get_wsgi_application()
