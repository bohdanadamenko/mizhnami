"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()

try:
    from whitenoise import WhiteNoise
    staticfiles_dir = Path(__file__).resolve().parent.parent / 'staticfiles'
    if staticfiles_dir.exists():
        application = WhiteNoise(application, root=str(staticfiles_dir), prefix='static/')
except ImportError:
    pass

app = application
