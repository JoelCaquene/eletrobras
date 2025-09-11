"""
ASGI config for CIGNA_GROUP project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

# Altere esta linha para apontar para o seu pacote de projeto principal
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CIGNA_GROUP.settings')

application = get_asgi_application()
