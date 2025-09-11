"""
ASGI config for CIGNA_GROUP project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

# A referência precisa ser para 'cigna_group' (em minúsculas)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cigna_group.settings')

application = get_asgi_application()
