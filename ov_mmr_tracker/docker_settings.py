"""
Settings to be used when project is used with Docker
"""

import os

from ov_mmr_tracker.settings import *

SECRET_KEY = os.getenv('SECRET_KEY', 'defaultsecretkey')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('DB_NAME', 'postgres'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', 'db'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

DEBUG = True if os.getenv('DEBUG', 'False') == 'True' else False

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS').split(',')