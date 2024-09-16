from server.settings.components import config
from server.settings.components.common import (
    INSTALLED_APPS,

)
from server.settings.environments.local import database

DEBUG = True

ALLOWED_HOSTS = [
    config('DOMAIN_NAME'),
    'localhost',
    '0.0.0.0',  # noqa: S104
    '127.0.0.1',
    '[::1]',
]

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
DATABASES = database

# Installed apps for development only:

INSTALLED_APPS += (
    # Linting migrations:
    # https://github.com/3YOURMIND/django-migration-linter
    'django_migration_linter',
)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
