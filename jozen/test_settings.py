"""
Test settings for CI/CD pipeline
"""
import os
from .settings import *

# Use PostgreSQL for testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DJANGO_DB_NAME', 'jozen_test'),
        'USER': os.environ.get('DJANGO_DB_USER', 'jozen_test'),
        'PASSWORD': os.environ.get('DJANGO_DB_PASSWORD', 'jozen_test_password'),
        'HOST': os.environ.get('DJANGO_DB_HOST', 'localhost'),
        'PORT': os.environ.get('DJANGO_DB_PORT', '5432'),
    }
}

# Disable logging during tests
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
}

# Use in-memory cache for testing
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Disable debug mode
DEBUG = False

# Set test secret key
SECRET_KEY = 'test-secret-key-for-ci'

# Allow all hosts for testing
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'testserver']

# Disable CSRF for testing
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False

# Use console email backend for testing
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Disable password validation for testing
AUTH_PASSWORD_VALIDATORS = []

# Use faster password hasher for testing
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]
